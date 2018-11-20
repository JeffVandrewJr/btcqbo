import shelve
import os
from copy import deepcopy
from rq import get_current_job
from flask import render_template, redirect, request
from app import app
import app.qbo as qbo
import app.btcp as btcp
from app.forms import BTCCodeForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/authqbo')
def authqbo():
    #calls fn to grab qbo auth url and then redirects there
    return redirect(qbo.get_auth_url())

@app.route('/qbologged')
def qbologged():
    #user is redirected here after qbo authorizes
    #sets the token values and real id globally using values passed in URL
    qbo.set_global_vars(
        realmid=request.args.get('realmId'),
        code=request.args.get('code'),
    )
    return "Logged"

@app.route('/authbtc', methods=['GET', 'POST'])
def authbtc():
    form = BTCCodeForm()
    if form.validate_on_submit():
        btcp.pairing(str(form.code.data))
        return render_template('success.html', output="success")
    return render_template('authbtc.html', title='Enter Code', form=form)    
@app.route('/postpayment')
def postpayment():
    return qbo.post_payment()

@app.route('/refresh')
def test_refresh():
    data = shelve.open('data')
    old_token = deepcopy(data['access_token'])
    data.close()
    qbo.refresh_stored_tokens()
    data = shelve.open('data')
    new_token = data['access_token']
    data.close()
    return 'done'

@app.route('/testinvoice')
def test_invoice():
    data = shelve.open('data')
    btc_client = data['btc_client']
    data.close()
    invoice = btc_client.create_invoice({"price": 477.5, "currency": "USD", "orderId": 1065, "buyer.email": "jeffvandrew@yahoo.com"})
    return "class is" + invoice.__class__.__name__ + " and data is: " + str(invoice)
    
