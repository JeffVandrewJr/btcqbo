from app import app
import os
import time
from app.utils import save, fetch
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects.account import Account
from quickbooks.objects.base import Ref
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment, PaymentLine
from quickbooks.objects.paymentmethod import PaymentMethod

callback_url = os.getenv('CALLBACK_URL')


def post_payment(doc_number="", amount=0):
    refresh_stored_tokens()
    qb = fetch('qbclient')
    pmt_method_list = PaymentMethod.filter(
        Name="BTCPay",
        qb=qb
    )
    try:
        pmt_method = pmt_method_list[0]
    except IndexError:
        new_pmt_method = PaymentMethod()
        new_pmt_method.Name = "BTCPay"
        new_pmt_method.save(qb=qb)
        pmt_method_list = PaymentMethod.filter(
            Name="BTCPay",
            qb=qb
        )
        pmt_method = pmt_method_list[0]
    deposit_acct_list = Account.filter(
        Name="Bitcoin-BTCPay",
        qb=qb
    )
    try:
        deposit_acct = deposit_acct_list[0]
    except IndexError:
        new_acct = Account()
        new_acct.Name = "Bitcoin-BTCPay"
        new_acct.AccountSubType = "OtherCurrentAssets"
        new_acct.save(qb=qb)
        deposit_acct_list = Account.filter(
            Name="Bitcoin-BTCPay",
            qb=qb
        )
        deposit_acct = deposit_acct_list[0]
    invoice_list = Invoice.filter(DocNumber=doc_number, qb=qb)
    try:
        invoice = invoice_list[0]
    except IndexError:
        return "No Such Invoice"
    else:
        linked_invoice = invoice.to_linked_txn()
        payment_line = PaymentLine()
        payment_line.Amount = amount
        payment_line.LinkedTxn.append(linked_invoice)
        payment = Payment()
        payment.TotalAmt = amount
        payment.CustomerRef = invoice.CustomerRef
        deposit_account_ref = Ref()
        deposit_account_ref.value = deposit_acct.Id
        pmt_method_ref = Ref()
        pmt_method_ref.name = pmt_method.Name
        payment.PaymentMethodRef = pmt_method_ref
        payment.DepositToAccountRef = deposit_account_ref
        payment.Line.append(payment_line)
        payment.save(qb=qb)
        return "Payment Made: " + str(payment)


def get_auth_url():
    session_manager = Oauth2SessionManager(
        client_id=os.getenv('QUICKBOOKS_CLIENT_ID'),
        client_secret=os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        base_url=callback_url,
    )
    authorize_url = session_manager.get_authorize_url(callback_url)
    return authorize_url


def set_global_vars(realmid, code):
    session_manager = Oauth2SessionManager(
        client_id=os.getenv('QUICKBOOKS_CLIENT_ID'),
        client_secret=os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        base_url=callback_url,
    )
    realm_id = realmid
    session_manager.get_access_tokens(code)
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
    session_manager = Oauth2SessionManager(
        client_id=realm_id,
        client_secret=os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        access_token=access_token,
    )
    sandbox = False
    if os.getenv('QUICKBOOKS_SANDBOX') == 'True':
        sandbox = True
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
    if '1' not in app.task_queue.job_ids:
        app.task_queue.enqueue_call(func=repeat_refresh, timeout=-1, job_id='1')


def refresh_stored_tokens():
    realm_id = fetch('realm_id')
    session_manager = Oauth2SessionManager(
        client_id=os.getenv('QUICKBOOKS_CLIENT_ID'),
        client_secret=os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        base_url=callback_url,
        access_token=fetch('access_token'),
        refresh_token=fetch('refresh_token'),
    )
    result = session_manager.refresh_access_tokens(return_result=True)
    save('access_token', session_manager.access_token)
    save('refresh_token', session_manager.refresh_token)
    session_manager = Oauth2SessionManager(
        client_id=realm_id,
        client_secret=os.getenv('QUICKBOOKS_CLIENT_SECRET'),
        access_token=fetch('access_token'),
    )
    sandbox = False
    if os.getenv('QUICKBOOKS_SANDBOX') == 'True':
        sandbox = True
    qbclient = QuickBooks(
        sandbox=sandbox,
        session_manager=session_manager,
        company_id=realm_id
    )
    QuickBooks.enable_global()
    save('session_manager', session_manager)
    save('qbclient', qbclient)
    return str(result)


def verify_invoice(doc_number="", email=""):
    qb = fetch('qbclient')
    invoice_list = Invoice.filter(DocNumber=doc_number, qb=qb)
    customers = Customer.filter(id=invoice_list[0].CustomerRef.value, qb=qb)
    if customers[0].PrimaryEmailAddr.Address.lower() == email.lower():
        return True
    else:
        return False


def repeat_refresh():
    while True:
        time.sleep(3000)
        refresh_stored_tokens()
