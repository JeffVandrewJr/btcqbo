import os
from flask import url_for
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment, PaymentLine

callback_url = 'http://localhost:5000/qbologged'

def post_payment():
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
    invoice_list = Invoice.filter(DocNumber="1036", qb=client)
    linked_invoice = invoice_list[0].to_linked_txn()
    payment_line = PaymentLine()
    payment_line.Amount = 477.5
    payment_line.LinkedTxn.append(linked_invoice)
    payment = Payment()
    payment.TotalAmt = 477.5
    payment.CustomerRef = invoice_list[0].CustomerRef 
    payment.Line.append(payment_line)
    payment.save(qb=client)
    return str(payment)

def get_auth_url():
    session_manager = Oauth2SessionManager(
        client_id = os.environ['QUICKBOOKS_CLIENT_ID'],
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        base_url = callback_url,
    )
    authorize_url = session_manager.get_authorize_url(callback_url)
    return authorize_url

def set_global_vars(realmid, code):
    session_manager = Oauth2SessionManager(
        client_id = os.environ['QUICKBOOKS_CLIENT_ID'],
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        base_url = callback_url,
    )
    global realm_id
    realm_id = realmid
    global access_token
    global refresh_token
    session_manager.get_access_tokens(code)
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
