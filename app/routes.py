import os
from flask import render_template, redirect, request, abort
from app import app
import app.qbo as qbo
import app.btcp as btcp
from app.forms import BTCCodeForm


@app.route('/')
@app.route('/index')
def index():
    if os.getenv('AUTH_ACCESS') == 'True':
        return render_template('index.html')
    else:
        return str(os.getenv('AUTH_ACCESS'))


@app.route('/authqbo')
def authqbo():
    # calls fn to grab qbo auth url and then redirects there
    if os.getenv('AUTH_ACCESS') == 'True':
        return redirect(qbo.get_auth_url())
    else:
        return "Access Denied"


@app.route('/qbologged')
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


@app.route('/authbtc', methods=['GET', 'POST'])
def authbtc():
    if os.getenv('AUTH_ACCESS') == 'True':
        form = BTCCodeForm()
        if form.validate_on_submit():
            btcp.pairing(str(form.code.data))
            return render_template('success.html', output="success")
        return render_template('authbtc.html', title='Enter Code', form=form)    
    else:
        return "Access Denied"


@app.route('/api/v1/payment', methods=['POST'])
def paymentapi():
    if not request.json or not 'id' in request.json:
        abort(400)
    btc_client = fetch('btc_client')
    invoice = btc_client.get_invoice(request.json['id'])
    if invoice['status'] == "complete":
        doc_number = invoice['orderId']
        amount = float(invoice['price']) 
        if amount > 0 and doc_number != None: 
            post_payment(doc_number=str(doc_number), amount=amount) 
            return "Payment Accepted", 201
        else:
            return "Payment Amount was zero or doc number was invalid", 200
    else:
        return "Good request, but JSON states payment not yet confirmed", 200

@app.route('/test')
def test():
    payment = qbo.post_payment(doc_number="1036", amount=477.5)
    return payment
