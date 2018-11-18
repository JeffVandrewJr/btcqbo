import os
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
    return str(qbo.access_token) + "  |  " + str(qbo.refresh_token)

@app.route('/authbtc', methods=['GET', 'POST'])
def authbtc():
    form = BTCCodeForm()
    if form.validate_on_submit():
        btcp.pairing('qcAAZjZ')
        return str(data['btc_token'])
    return render_template('authbtc.html', title='Enter Code', form=form)    
@app.route('/postpayment')
def postpayment():
    return qbo.post_payment()
