from app import app
from app.utils import save, fetch
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects.account import Account
from quickbooks.objects.base import Ref
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment, PaymentLine
from quickbooks.objects.paymentmethod import PaymentMethod
import time


def post_payment(doc_number="", amount=0):
    # post payment to QBO
    # requires passing invoice number and pmt amt as arguments
    refresh_stored_tokens()
    qb = fetch('qbclient')
    # check if BTCPay is already in QBO as a pmt method
    pmt_method_list = PaymentMethod.filter(
        Name="BTCPay",
        qb=qb
    )
    try:
        # if BTCPay is already in QBO, set it as pmt method
        pmt_method = pmt_method_list[0]
    except IndexError:
        # if BTCPay is not in QBO, create it as pmt method
        new_pmt_method = PaymentMethod()
        new_pmt_method.Name = "BTCPay"
        new_pmt_method.save(qb=qb)
        # set newly created BTCPay pmt method as pmt method
        pmt_method_list = PaymentMethod.filter(
            Name="BTCPay",
            qb=qb
        )
        pmt_method = pmt_method_list[0]
    # check if QBO has asset acct for Bitcoin-BTCPay
    deposit_acct_list = Account.filter(
        Name="Bitcoin-BTCPay",
        qb=qb
    )
    try:
        # if Bitcoin-BTCPay is in QBO, set as deposit acct
        deposit_acct = deposit_acct_list[0]
    except IndexError:
        # if Bitcoin-BTCPay is not in QBO, create it as deposit acct
        new_acct = Account()
        new_acct.Name = "Bitcoin-BTCPay"
        new_acct.AccountSubType = "OtherCurrentAssets"
        new_acct.save(qb=qb)
        # set newly created Bitcoin-BTCPay acct as deposit acct
        deposit_acct_list = Account.filter(
            Name="Bitcoin-BTCPay",
            qb=qb
        )
        deposit_acct = deposit_acct_list[0]
    # pull list of invoice objects matching invoice number from QBO
    invoice_list = Invoice.filter(DocNumber=doc_number, qb=qb)
    try:
        # only one invoice can match the inv #, so pull it from list
        invoice = invoice_list[0]
    except IndexError:
        return "No Such Invoice"
    else:
        # convert invoice object to linked invoice object
        linked_invoice = invoice.to_linked_txn()
        payment_line = PaymentLine()
        payment_line.Amount = amount
        # attach linked invoice object to payment line object
        payment_line.LinkedTxn.append(linked_invoice)
        payment = Payment()
        payment.TotalAmt = amount
        payment.CustomerRef = invoice.CustomerRef
        # create deposit acct reference object from deposit acct object
        deposit_account_ref = Ref()
        deposit_account_ref.value = deposit_acct.Id
        # create pmt method reference object from pmt method object
        pmt_method_ref = Ref()
        pmt_method_ref.name = pmt_method.Name
        # attach pmt method ref, dep acct ref, and pmt line obj to pmt obj
        payment.PaymentMethodRef = pmt_method_ref
        payment.DepositToAccountRef = deposit_account_ref
        payment.Line.append(payment_line)
        payment.save(qb=qb)
        return "Payment Made: " + str(payment)


def get_auth_url():
    # asks Intuit server for a valid authorization URL
    # returns authorization URL
    callback_url = app.config.get('CALLBACK_URL')
    session_manager = Oauth2SessionManager(
        client_id=fetch('qb_id'),
        client_secret=fetch('qb_secret'),
        base_url=callback_url,
    )
    authorize_url = session_manager.get_authorize_url(callback_url)
    return authorize_url


def set_global_vars(realmid, code):
    # stores Intuit tokens
    # stores QBO client object
    # stores session manager object for future token refreshes
    callback_url = app.config.get('CALLBACK_URL')
    session_manager = Oauth2SessionManager(
        client_id=fetch('qb_id'),
        client_secret=fetch('qb_secret'),
        base_url=callback_url,
    )
    realm_id = realmid
    data = session_manager.get_access_tokens(
        auth_code=code,
        return_result=True,
    )
    # sanity check: if no valid response from Intuit, abort fn
    if 'token_type' not in data:
        return None
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
    session_manager = Oauth2SessionManager(
        client_id=realm_id,
        client_secret=fetch('qb_secret'),
        access_token=access_token,
    )
    sandbox = fetch('qb_sandbox')
    qbclient = QuickBooks(
        sandbox=sandbox,
        session_manager=session_manager,
        company_id=realm_id
    )
    QuickBooks.enable_global()
    save('realm_id', realm_id)
    save('access_token', access_token)
    save('refresh_token', refresh_token)
    save('session_manager', session_manager)
    save('qbclient', qbclient)
    # add refresh job to RQ
    add_job()


def refresh_stored_tokens():
    # refresh stored QBO tokens
    callback_url = app.config.get('CALLBACK_URL')
    realm_id = fetch('realm_id')
    session_manager = Oauth2SessionManager(
        client_id=fetch('qb_id'),
        client_secret=fetch('qb_secret'),
        base_url=callback_url,
        access_token=fetch('access_token'),
        refresh_token=fetch('refresh_token'),
    )
    result = session_manager.refresh_access_tokens(return_result=True)
    save('access_token', session_manager.access_token)
    save('refresh_token', session_manager.refresh_token)
    session_manager = Oauth2SessionManager(
        client_id=realm_id,
        client_secret=fetch('qb_secret'),
        access_token=fetch('access_token'),
    )
    sandbox = fetch('qb_sandbox')
    qbclient = QuickBooks(
        sandbox=sandbox,
        session_manager=session_manager,
        company_id=realm_id
    )
    QuickBooks.enable_global()
    save('session_manager', session_manager)
    save('qbclient', qbclient)
    # add refresh job to RQ if not already there
    add_job()
    return str(result)


def verify_invoice(doc_number="", email=""):
    # checks QBO to ensure invoice number matches email provided
    # if match, returns QBO customer object attached to invoice
    # if mismatch, returns None
    refresh_stored_tokens()
    qb = fetch('qbclient')
    invoice_list = Invoice.filter(DocNumber=doc_number, qb=qb)
    customers = Customer.filter(id=invoice_list[0].CustomerRef.value, qb=qb)
    if customers[0].PrimaryEmailAddr.Address.lower() == email.lower():
        return customers[0]
    else:
        return None


def repeat_refresh():
    # repeatedly refresh QBO tokens every 50 minutes
    # necessary bc Intuit is vague about token expirations
    while True:
        time.sleep(3000)
        refresh_stored_tokens()


def add_job():
    # check if repeat_refresh() is in RQ
    # if not in RQ, adds the job to RQ
    if '1' not in app.task_queue.job_ids:
        app.task_queue.enqueue_call(
                func=repeat_refresh,
                timeout=-1, job_id='1'
                )
