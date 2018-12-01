import os
from flask import render_template, redirect, request, abort, url_for, Response
from werkzeug.security import check_password_hash
from app import app
from app import auth
import app.qbo as qbo
import app.btcp as btcp
from app.utils import fetch
from app.forms import BTCCodeForm
from rq_dashboard import blueprint


if os.getenv('RQ_ACCESS') == 'True':
    @blueprint.before_request
    def rq_login():
        auth = request.authorization
        if (auth is None or not check_password_hash(fetch('hash'), auth.password or
                fetch('username') != auth.username)):
            return Response("Authentication Failed", 401)
        elif (fetch('username') == auth.username and
                check_password_hash(fetch('hash'), auth.password)):
            pass
        else:
            return redirect(url_for('index'))
    app.register_blueprint(
        blueprint,
        url_prefix="/btcqbo/rq",
    )


@auth.verify_password
def verify_password(username, pswd):
    if fetch('username') == username:
        return check_password_hash(fetch('hash'), pswd)
    else:
        return False


@app.route('/btcqbo/index')
@auth.login_required
def index():
    if os.getenv('AUTH_ACCESS') == 'True':
        return render_template('index.html')
    else:
        return "Access Denied"


@app.route('/btcqbo/authqbo')
@auth.login_required
def authqbo():
    # calls fn to grab qbo auth url and then redirects there
    if os.getenv('AUTH_ACCESS') == 'True':
        return redirect(qbo.get_auth_url())
    else:
        return "Access Denied"


@app.route('/btcqbo/qbologged')
def qbologged():
    # user is redirected here after qbo authorizes
    # sets the token values and real id globally using values passed in URL
    if os.getenv('AUTH_ACCESS') == 'True':
        qbo.set_global_vars(
            realmid=request.args.get('realmId'),
            code=request.args.get('code'),
        )
        return "Logged"
    else:
        return "Access Denied"


@app.route('/btcqbo/authbtc', methods=['GET', 'POST'])
@auth.login_required
def authbtc():
    if os.getenv('AUTH_ACCESS') == 'True':
        form = BTCCodeForm()
        if form.validate_on_submit():
            btcp.pairing(str(form.code.data))
            return render_template('success.html', output="success")
        return render_template('authbtc.html', title='Enter Code', form=form)
    else:
        return "Access Denied"


@app.route('/btcqbo/api/v1/payment', methods=['GET', 'POST'])
def paymentapi():
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
            else:
                return "Payment not yet confirmed.", 200
        else:
            return "No payment status received.", 400
    else:
        return "Invalid transaction ID.", 400


@app.route('/btcqbo/verify', methods=['POST'])
def verify():
    data = request.form
    customer = qbo.verify_invoice(
        doc_number=str(data['orderId']),
        email=str(data['email'])
    )
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
            "notificationEmail": data['email'],
            "orderId": data['orderId'],
            "notificationURL": data['notificationUrl'],
            "redirectURL": data['redirectUrl']
        })
        inv_url = inv_data['url']
        return redirect(inv_url)
    else:
        return "The email and invoice number provided do not match. Please try again. If multiple emails are associated to the invoice, you must use the primary one."
