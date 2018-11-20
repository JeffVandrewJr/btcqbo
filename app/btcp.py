from btcpay import BTCPayClient
import shelve
from btcpay.crypto import generate_privkey

btcpay_host = 'https://btcpay.vandrew.com'

def pairing(code):
    privkey = generate_privkey()
    btc_client = BTCPayClient(host=btcpay_host, pem=privkey)
    btc_token = btc_client.pair_client(code)
    btc_client = BTCPayClient(host=btcpay_host, pem=privkey, tokens=btc_token)
    with shelve.open('data', 'c') as data:
        data['btc_token'] = btc_token
        data['btc_client'] = btc_client
        data['privkey'] = privkey
