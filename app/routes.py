import shelve
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
    data = shelve.open('data')
    return str(data['access_token']) + "  |  " + str(data['refresh_token'])
    data.close()

@app.route('/authbtc', methods=['GET', 'POST'])
def authbtc():
    form = BTCCodeForm()
    data = shelve.open('data')
    if form.validate_on_submit():
        btcp.pairing('qcAAZjZ')
        output = str(data['btc_token'])
        data.close()
        return output
    return render_template('authbtc.html', title='Enter Code', form=form)    
@app.route('/postpayment')
def postpayment():
    return qbo.post_payment()
