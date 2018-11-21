import os
from flask import render_template, redirect, request
from app import app
import app.qbo as qbo
import app.btcp as btcp
from app.forms import BTCCodeForm
from app.utils import save, fetch

@app.route('/')
@app.route('/index')
def index():
    if os.environ['AUTH_ACCESS'] == 'True':
        return render_template('index.html')
    else:
        return "Access Denied"

@app.route('/authqbo')
def authqbo():
    #calls fn to grab qbo auth url and then redirects there
    if os.environ['AUTH_ACCESS'] == 'True':
        return redirect(qbo.get_auth_url())
    else:
        return "Access Denied"

@app.route('/qbologged')
def qbologged():
    #user is redirected here after qbo authorizes
    #sets the token values and real id globally using values passed in URL
    if os.environ['AUTH_ACCESS'] == 'True':
        qbo.set_global_vars(
            realmid=request.args.get('realmId'),
            code=request.args.get('code'),
        )
        return "Logged"
    else:
        return "Access Denied"

@app.route('/authbtc', methods=['GET', 'POST'])
def authbtc():
    if os.environ['AUTH_ACCESS'] == 'True':
        form = BTCCodeForm()
        if form.validate_on_submit():
            btcp.pairing(str(form.code.data))
            return render_template('success.html', output="success")
        return render_template('authbtc.html', title='Enter Code', form=form)    
    else:
        return "Access Denied"

@app.route('/postpayment')
def postpayment():
    return qbo.post_payment()

@app.route('/refresh')
def test_refresh():
    old_token = fetch('access_token')
    qbo.refresh_stored_tokens()
    new_token = fetch('access_token')
    return 'done'

@app.route('/testinvoice')
def test_invoice():
    btc_client = fetch('btc_client')
    invoice = btc_client.create_invoice({"price": 477.5, "currency": "USD", "orderId": 1065, "buyer": {"email": "jeffvandrew@yahoo.com"}})
    return "class is" + invoice.__class__.__name__ + " and URL is: " + str(invoice['url'])
    
