import btcpay
import os
from flask import render_template, redirect, request
from app import app
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment, PaymentLine
from btcpay import BTCPayClient 

callback_url = 'http://localhost:5000/qbologged'
access_token = None
refresh_token = None
realm_id = None

@app.route('/')
@app.route('/index')
def index():
    session_manager = Oauth2SessionManager(
        client_id = realm_id,
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        access_token = access_token,
    )
    client = QuickBooks(
        sandbox = True,
        session_manager=session_manager,
        company_id=realm_id
    )
    QuickBooks.enable_global()
    invoice = Invoice.filter(DocNumber=1036, qb=client)
    linked_invoice = invoice.to_linked_txn()
    payment_line = PaymentLine()
    payment_line.Amount = 477.50
    payment_line.LinkedTxn = linked_invoice
    payment = Payment()
    payment.Line[0] = payment_line
    payment.save(qb=client)

@app.route('/authqbo')
def authqbo():
    session_manager = Oauth2SessionManager(
        client_id = os.environ['QUICKBOOKS_CLIENT_ID'],
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        base_url = callback_url,
    )
    authorize_url = session_manager.get_authorize_url(callback_url)
    return redirect(authorize_url)

@app.route('/qbologged')
def qbologged():
    session_manager = Oauth2SessionManager(
        client_id = os.environ['QUICKBOOKS_CLIENT_ID'],
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        base_url = callback_url,
    )
    global realm_id
    realm_id = request.args.get('realmId')
    code = request.args.get('code') #this is a flask thing for pulling query string arguments from the URL route
    global access_token
    global refresh_token
    session_manager.get_access_tokens(code)
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
    return str(access_token) + "  |  " + str(refresh_token)
