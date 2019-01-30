from app import app
import app.qbo as qbo
from app.utils import fetch, save, login, send, repeat_ipn
from app.forms import BTCCodeForm, KeysForm, MailForm
from btcpay import BTCPayClient
from flask import render_template, redirect, request, url_for, flash
import os
import requests
from threading import Thread
from urllib.parse import urljoin


@app.route('/btcqbo/')
@app.route('/btcqbo/index')
def index():
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    return render_template('index.html')


@app.route('/btcqbo/setkeys', methods=['GET', 'POST'])
def set_keys():
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    form = KeysForm()
    if form.validate_on_submit():
        save('qb_id', form.qb_id.data)
        save('qb_secret', form.qb_secret.data)
        save('qb_sandbox', form.qb_sandbox.data)
        return redirect(url_for('authqbo'))
    return render_template(
        'setkeys.html',
        title='Set Intuit Keys',
        form=form
    )


@app.route('/btcqbo/authqbo')
def authqbo():
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    # calls fn to grab qbo auth url and then redirects there
    if fetch('qb_secret') is not None:
        return redirect(qbo.get_auth_url())
    else:
        return redirect(url_for('set_keys'))


@app.route('/btcqbo/qbologged')
def qbologged():
    # user is redirected here after qbo authorizes
    qbo.set_global_vars(
        realmid=request.args.get('realmId'),
        code=request.args.get('code'),
    )
    flash('Sync to QBO Successful.')
    return render_template('index.html')


@app.route('/btcqbo/authbtc', methods=['GET', 'POST'])
def authbtc():
    # accepts BTCPay pairing code and calls pairing fn
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    form = BTCCodeForm()
    url = urljoin(str(os.getenv('BTCPAY_HOST')), 'api-tokens')
    if form.validate_on_submit():
        client = BTCPayClient.create_client(
                host=app.config.get('BTCPAY_HOST'),
                code=form.code.data,
        )
        save('btc_client', client)
        save('forward_url', form.forward_url.data)
        flash('Pairing to BTCPay Successful')
        return render_template('index.html')
    return render_template(
        'authbtc.html',
        title='Enter Code',
        form=form,
        url=url
    )


@app.route('/btcqbo/mail', methods=['GET', 'POST'])
def setmail():
    # sets user email settings
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    form = MailForm()
    if form.validate_on_submit():
        save('mail_on', form.mail_on.data)
        save('mail_user', str(form.mail_user.data))
        save('mail_pswd', str(form.mail_pswd.data))
        save('mail_host', str(form.mail_host.data))
        save('mail_port', int(form.mail_port.data))
        save('mail_from', str(form.mail_from.data))
        save('merchant', str(form.merchant.data))
        if form.recipient.data is not None and str(form.recipient.data) != "":
            try:
                send(
                    dest=form.recipient.data,
                    qb_inv='test',
                    btcp_inv='test',
                    amt=0.00,
                )
            except Exception as e:
                app.logger.exception(e)
                flash('Connection to SMTP server failed.')
                return render_template('index.html')
            flash('Test email sent.')
        else:
            flash('Email settings updated.')
        return render_template('index.html')
    return render_template(
        'setmail.html',
        title='Email Settings',
        form=form,
    )


@app.route('/btcqbo/api/v1/payment', methods=['GET', 'POST'])
def paymentapi():
    # receives and processes invoice notifications from BTCPay
    if not request.json:
        return "No JSON Data.", 200
    elif 'status' in request.json:
        app.logger.info(f'IPN: {request.json["status"]} {request.json["id"]}')
        # check for duplicates
        if app.redis.get(request.json['id']) is not None:
            return "Duplicate IPN", 200
        btc_client = fetch('btc_client')
        invoice = btc_client.get_invoice(request.json['id'])
        if not isinstance(invoice, dict):
            return "Spam IPN", 200
        if invoice['status'] == 'paid' and fetch('mail_on'):
            # emails buyer when invoice is "paid"
            dest = invoice['buyer']['email']
            qb_inv = invoice['orderId']
            btcp_inv = invoice['id']
            amt = float(invoice['price'])
            send(dest, qb_inv, btcp_inv, amt)
            return "Buyer email sent.", 200
        elif invoice['status'] == 'confirmed' or \
                invoice['status'] == 'complete':
            # ping BTCPay to confirm IPN real, then post payment
            doc_number = invoice['orderId']
            amount = float(invoice['price'])
            if amount > 0 and doc_number is not None:
                qbo.post_payment(
                        doc_number=str(doc_number),
                        amount=amount,
                        btcp_id=invoice['id']
                        )
                if fetch('mail_on'):
                    dest = invoice['buyer']['email']
                    qb_inv = invoice['orderId']
                    btcp_inv = invoice['id']
                    amt = float(invoice['price'])
                    send(dest, qb_inv, btcp_inv, amt)
                return "Payment Accepted", 201
            else:
                return "Payment was zero or invalid invoice #.", 200
        else:
            return "IPN received.", 200
    else:
        return "Ignore.", 200


@app.route('/btcqbo/api/v1/deposit', methods=['GET', 'POST'])
def deposit_api():
    # receives and processes deposit notifications from BTCPay
    # forward all IPNs
    forward_url = fetch('forward_url')
    if forward_url is not None and forward_url != '':
        r = requests.post(forward_url, json=request.get_json())
        if not r.ok:
            app.logger.error(f'IPN Rejected by Forwarding URL: \
                    {r.status_code}, {r.url}, {r.reason}, {r.text}')
            Thread(
                    target=repeat_ipn,
                    args=(forward_url, request.get_json())
                    ).start()
    if not request.json:
        return "No JSON Data.", 200
    elif 'status' in request.json:
        app.logger.info(f'IPN: {request.json["status"]} {request.json["id"]}')
        # check for duplicates
        if app.redis.get(request.json['id']) is not None:
            return "Duplicate IPN", 200
        btc_client = fetch('btc_client')
        deposit = btc_client.get_invoice(request.json['id'])
        if not isinstance(deposit, dict):
            return "Spam IPN", 200
        if deposit['status'] == 'confirmed' or \
                deposit['status'] == 'complete':
            # then post deposit
            amount = deposit.get('price')
            tax = deposit.get('taxIncluded')
            if amount is None:
                return "No Payment to Record.", 200
            if tax is None:
                tax = 0
            btcp_id = str(deposit.get('id'))
            qbo.post_deposit(
                    amount=float(amount),
                    tax=float(tax),
                    btcp_id=btcp_id,
                )
            return "Payment Accepted", 201
        else:
            return "IPN received.", 200
    else:
        return "Ignore.", 200


@app.route('/btcqbo/verify', methods=['POST'])
def verify():
    # receives/processes form data from public facing pmt page
    data = request.form
    customer = qbo.verify_invoice(
        doc_number=str(data['orderId']),
        email=str(data['email'])
    )
    # create BTCPay invoice from submitted form data
    if customer is not None:
        btc_client = fetch('btc_client')
        inv_data = btc_client.create_invoice({
            "price": data['amount'],
            "currency": "USD",
            "buyer": {
                "name": customer.DisplayName,
                "email": data['email'],
            },
            "orderId": data['orderId'],
            "fullNotifications": True,
            "notificationURL": data['notificationUrl'],
            "redirectURL": data['redirectUrl']
        })
        inv_url = inv_data['url']
        return redirect(inv_url)
    else:
        no_match = '''
        The email and invoice number provided do not match.
         Please try again. If multiple emails are associated to
         the invoice, you must use the primary one.
        '''
        return no_match
