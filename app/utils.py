from app import app
from email.message import Message
import os
import pickle
import requests
import smtplib
import time
from urllib.parse import urljoin


def save(key, object):
    # pickles an object and saves it to redis at the key passed as arg
    pickled_object = pickle.dumps(object)
    app.redis.set(key, pickled_object)


def fetch(key):
    # checks redis for picked object at key passed as argument
    # if finds object, unpickles and returns it
    # if no object at given key, returns None
    item = app.redis.get(key)
    if item is None:
        return None
    else:
        return pickle.loads(item)


def wipe(key):
    # wipes all redis data stored at a given key
    app.redis.delete(key)


def login(cookies):
    # checks if user is logged into BTCPay as admin
    # checks by making get request on BTCPay protected resource
    # if user user is logged in to BTCPay, returns None
    # if user is not logged into BTCPay, returns BTCPay URL to log in
    url = urljoin(str(os.getenv('BTCPAY_HOST')), 'server/users')
    response = requests.get(url, cookies=cookies)
    try:
        first = response.history[0]
    except IndexError:
        first = response
    if first.status_code == 200:
        return None
    else:
        initial_url = urljoin(str(os.getenv('BTCPAY_HOST')), 'Account/Login')
        full_url = initial_url + '?ReturnUrl=%2Fbtcqbo%2Findex'
        return full_url


def repeat_ipn(forward_url, json):
    r = requests.post(forward_url, json=json)
    counter = 0
    while not r.ok:
        app.logger.error(f'IPN Rejected by Forwarding URL: \
                {r.status_code}, {r.url}, {r.reason}, {r.text}')
        r = requests.post(forward_url, json=json)
        counter += 1
        if counter > 3:
            break
        time.sleep(300)


def send(dest, qb_inv, btcp_inv, amt):
    # emails receipt to customer
    merchant = fetch('merchant')
    msg = Message()
    msg['subject'] = f'Receipt from {merchant}'
    msg['to'] = dest
    msg['from'] = fetch('mail_from')
    body = f'''
    Amount Paid: ${amt}\n
    Invoice Number: {qb_inv}\n
    Confirmation ID: {btcp_inv}
    '''
    msg.set_payload(body)
    smtp = smtplib.SMTP(
        host=fetch('mail_host'),
        port=fetch('mail_port'),
        timeout=7,
    )
    smtp.ehlo()
    if fetch('mail_port') == 587:
        smtp.starttls()
    smtp.login(fetch('mail_user'), fetch('mail_pswd'))
    smtp.send_message(msg=msg, from_addr=fetch('mail_from'), to_addrs=dest)
    smtp.quit()
