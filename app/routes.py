import os
from urllib.parse import urljoin
from flask import render_template, redirect, request, abort, url_for, flash
from app import app
import app.qbo as qbo
import app.btcp as btcp
from app.utils import fetch, save, login, send
from app.forms import BTCCodeForm, KeysForm, MailForm
from rq_dashboard import blueprint


if os.getenv('RQ_ACCESS') == 'True':
    @blueprint.before_request
    # decorator modifies the blueprint imported from rq_dashboard
    # modification is that before a request, this authorization fn is run
    def rq_login():
        status = login(request.cookies)
        if status is not None:
            return redirect(status)
    # after adding before_request to preset blueprint, register the blueprint
    app.register_blueprint(
        blueprint,
        url_prefix="/btcqbo/rq",
    )


@app.route('/btcqbo/')
@app.route('/btcqbo/index')
def index():
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    if os.getenv('AUTH_ACCESS') == 'True':
        return render_template('index.html')
    else:
        return "Access Denied"


@app.route('/btcqbo/setkeys', methods=['GET', 'POST'])
def set_keys():
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    if os.getenv('AUTH_ACCESS') == 'True':
        form = KeysForm()
        if form.validate_on_submit():
            save('qb_id', form.qb_id.data)
            save('qb_secret', form.qb_secret.data)
            save('qb_sandbox', form.qb_sandbox.data)
            return render_template('keysset.html')
        return render_template(
            'setkeys.html',
            title='Set Intuit Keys',
            form=form
        )
    else:
        return "Access Denied."


@app.route('/btcqbo/authqbo')
def authqbo():
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    # calls fn to grab qbo auth url and then redirects there
    if os.getenv('AUTH_ACCESS') == 'True':
        if fetch('qb_secret') is not None:
            return redirect(qbo.get_auth_url())
        else:
            return redirect(url_for('set_keys'))
    else:
        return "Access Denied."


@app.route('/btcqbo/qbologged')
def qbologged():
    # user is redirected here after qbo authorizes
    if os.getenv('AUTH_ACCESS') == 'True':
        qbo.set_global_vars(
            realmid=request.args.get('realmId'),
            code=request.args.get('code'),
        )
        qbo.add_job()
        return render_template('success.html')
    else:
        return "Access Denied"


@app.route('/btcqbo/authbtc', methods=['GET', 'POST'])
def authbtc():
    # accepts BTCPay pairing code and calls pairing fn
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    if os.getenv('AUTH_ACCESS') == 'True':
        form = BTCCodeForm()
        url = urljoin(str(os.getenv('BTCPAY_HOST')), 'api-tokens')
        if form.validate_on_submit():
            btcp.pairing(str(form.code.data))
            return render_template('success.html')
        return render_template(
            'authbtc.html',
            title='Enter Code',
            form=form,
            url=url
        )
    else:
        return "Access Denied"


@app.route('/btcqbo/mail')
def setmail():
    # sets user email settings
    status = login(request.cookies)
    if status is not None:
        return redirect(status)
    if os.getenv('AUTH_ACCESS') == 'True':
        form = MailForm()
        if form.validate_on_submit():
            save('mail_on', form.mail_on.data)
            save('mail_user', form.mail_user.data)
            save('mail_pswd', form.mail_pswd.data)
            save('mail_host', form.mail_host.data)
            save('mail_port', int(form.mail_port.data))
            save('mail_from', form.mail_from.data)
            save('merchant', form.merchant.data)
            if form.recipient.data is not None and form.recipient.data != "":
                send(
                    dest=form.recipient.data,
                    qb_inv='test',
                    btcp_inv='test',
                    amt=0.00,
                )
                flash('Test email sent.')
            else:
                flash('Email settings updated.')
            return render_template('index.html')
        return render_template('setmail.html')
    else:
        return "Access Denied"


@app.route('/btcqbo/api/v1/payment', methods=['GET', 'POST'])
def paymentapi():
    # receives and processes pmt notifications from BTCPay
    if not request.json or 'id' not in request.json:
        abort(400)
    btc_client = fetch('btc_client')
    invoice = btc_client.get_invoice(request.json['id'])
    if isinstance(invoice, dict):
        if 'status' in invoice:
            if invoice['status'] == "confirmed":
                doc_number = invoice['orderId']
                amount = float(invoice['price'])
                if amount > 0 and doc_number is not None:
                    qbo.post_payment(doc_number=str(doc_number), amount=amount)
                    return "Payment Accepted", 201
                else:
                    return "Payment was zero or invalid invoice #.", 200
            elif invoice['status'] == "paid" and fetch('mail_on'):
                # emails buyer when invoice is "paid"
                dest = invoice['buyer']['email']
                qb_inv = invoice['orderId']
                btcp_inv = invoice['id']
                amt = float(invoice['price'])
                send(dest, qb_inv, btcp_inv, amt)
                return "Buyer email sent.", 200
            else:
                return "Payment not yet confirmed.", 200
        else:
            return "No payment status received.", 400
    else:
        return "Invalid transaction ID.", 400


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
                "notify": True,
            },
            "orderId": data['orderId'],
            "notificationURL": data['notificationUrl'],
            "redirectURL": data['redirectUrl']
        })
        inv_url = inv_data['url']
        return redirect(inv_url)
    else:
        return "The email and invoice number provided do not match. Please try again. If multiple emails are associated to the invoice, you must use the primary one."
