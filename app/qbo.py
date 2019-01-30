from app import app, scheduler
from app.utils import save, fetch
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects.account import Account
from quickbooks.objects.base import Ref
from quickbooks.objects.deposit import Deposit, DepositLine, DepositLineDetail
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment, PaymentLine
from quickbooks.objects.paymentmethod import PaymentMethod


def post_payment(doc_number="", amount=0, btcp_id=''):
    # post payment to QBO
    '''
    doc_number: QBO invoice number
    amount: payment amount
    btcp_id: BTCPay invoice number
    '''
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
        app.logger.warning(f'No such invoice exists: {doc_number}')
        return None
    else:
        # convert invoice object to linked invoice object
        linked_invoice = invoice.to_linked_txn()
        description = 'BTCPay: ' + btcp_id
        payment_line = PaymentLine()
        payment_line.Amount = amount
        payment_line.Description = description
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
        # save payment to temp redis store to fliter duplicates
        app.redis.set(btcp_id, 'payment', ex=21600)
        return "Payment Made: " + str(payment)


def post_deposit(amount, tax, btcp_id):
    # post deposit to QBO
    if tax is None:
        tax = float(0)
    refresh_stored_tokens()
    qb = fetch('qbclient')
    # check if BTCPay income  acct is already in QBO
    income_acct_list = Account.filter(
        Name="BTCPay Sales",
        qb=qb
    )
    try:
        # if income acct exits, grab it
        income_acct = income_acct_list[0]
    except IndexError:
        # if income acct is not in QBO, create it
        new_acct = Account()
        new_acct.Name = "BTCPay Sales"
        new_acct.AccountSubType = "OtherPrimaryIncome"
        new_acct.save(qb=qb)
        # set newly created acct as income acct
        income_acct_list = Account.filter(
            Name="BTCPay Sales",
            qb=qb
        )
        income_acct = income_acct_list[0]
    # check if BTCPay Sales Tax acct is already in QBO
    sales_tax_acct_list = Account.filter(
        Name="Sales Tax from BTCPay",
        qb=qb
    )
    try:
        # if sales tax liability acct exits, grab it
        sales_tax_acct = sales_tax_acct_list[0]
    except IndexError:
        # if sales tax acct is not in QBO, create it
        new_acct = Account()
        new_acct.Name = "Sales Tax from BTCPay"
        new_acct.AccountSubType = "OtherCurrentLiabilities"
        new_acct.save(qb=qb)
        # set newly created acct as sales tax account
        sales_tax_acct_list = Account.filter(
            Name="Sales Tax from BTCPay",
            qb=qb
        )
        sales_tax_acct = sales_tax_acct_list[0]
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
    # create deposit
    description = 'BTCPay: ' + btcp_id
    income_acct_ref = Ref()
    income_acct_ref.value = income_acct.Id
    detail = DepositLineDetail()
    detail.AccountRef = income_acct_ref
    line = DepositLine()
    line.DepositLineDetail = detail
    deposit_account_ref = Ref()
    deposit_account_ref.value = deposit_acct.Id
    line.Amount = amount - tax
    line.Description = description
    # create sales tax line
    sales_tax_acct_ref = Ref()
    sales_tax_acct_ref.value = sales_tax_acct.Id
    line2 = DepositLine()
    detail2 = DepositLineDetail()
    detail2.AccountRef = sales_tax_acct_ref
    line2.DepositLineDetail = detail2
    line2.Description = description
    line2.Amount = tax
    deposit = Deposit()
    deposit.Line.append(line)
    deposit.Line.append(line2)
    deposit.DepositToAccountRef = deposit_account_ref
    deposit.save(qb=qb)
    # save payment to temp redis store to fliter duplicates
    app.redis.set(btcp_id, 'deposit', ex=21600)
    return 'Deposit Made: ' + str(deposit)


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

    @scheduler.task('interval', id='do_refresh', minutes=50)
    def refresh():
        if fetch('refresh_token') is not None:
            refresh_stored_tokens()
            app.logger.info('Scheduled QBO token refresh.')
        else:
            app.logger.info('QBO tokens not refreshed because no \
                    token stored.')


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
    return str(result)


def verify_invoice(doc_number="", email=""):
    # checks QBO to ensure invoice number matches email provided
    # if match, returns QBO customer object attached to invoice
    # if mismatch, returns None
    refresh_stored_tokens()
    qb = fetch('qbclient')
    invoice_list = Invoice.filter(DocNumber=doc_number, qb=qb)
    if invoice_list:
        customers = Customer.filter(
                id=invoice_list[0].CustomerRef.value, qb=qb)
    else:
        return None
    if customers:
        if customers[0].PrimaryEmailAddr.Address.lower() == email.lower():
            return customers[0]
        else:
            return None
    else:
        return None
