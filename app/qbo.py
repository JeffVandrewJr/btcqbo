from app import app
import os
import app.tasks as tasks
from app.utils import save, fetch
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment, PaymentLine

callback_url = os.getenv('CALLBACK_URL')

def post_payment():
    qb = fetch('qbclient')
    invoice_list = Invoice.filter(DocNumber="1036", qb=qb)
    linked_invoice = invoice_list[0].to_linked_txn()
    payment_line = PaymentLine()
    payment_line.Amount = 477.5
    payment_line.LinkedTxn.append(linked_invoice)
    payment = Payment()
    payment.TotalAmt = 477.5
    payment.CustomerRef = invoice_list[0].CustomerRef 
    payment.Line.append(payment_line)
    payment.save(qb=qb)
    return str(payment)

def get_auth_url():
    session_manager = Oauth2SessionManager(
        client_id = os.getenv('QUICKBOOKS_CLIENT_ID'),
        client_secret = os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        base_url = callback_url,
    )
    authorize_url = session_manager.get_authorize_url(callback_url)
    return authorize_url

def set_global_vars(realmid, code):
    session_manager = Oauth2SessionManager(
        client_id = os.getenv('QUICKBOOKS_CLIENT_ID'),
        client_secret = os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        base_url = callback_url,
    )
    realm_id = realmid
    session_manager.get_access_tokens(code)
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
    session_manager = Oauth2SessionManager(
        client_id = realm_id,
        client_secret = os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        access_token = access_token,
    )
    qbclient = QuickBooks(
        sandbox = True,
        session_manager=session_manager,
        company_id=realm_id
    )
    QuickBooks.enable_global()
    save('realm_id', realm_id)
    save('access_token', access_token)
    save('refresh_token', refresh_token)
    save('session_manager', session_manager)
    save('qbclient', qbclient)
    if '1' not in app.task_queue.job_ids:
        app.task_queue.enqueue_call(func=tasks.repeat_refresh, timeout=-1, job_id='1')
        
def refresh_stored_tokens():
    session_manager = fetch('session_manager')
    session_manager.refresh_access_tokens()
    save('access_token', session_manager.access_token)
    save('refresh_token', session_manager.refresh_token)
    save('session_manager', session_manager)

