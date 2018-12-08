import pickle
import requests
import os
from urllib.parse import urljoin
from app import app


def save(key, object):
    # pickles an object and saves it to redis at the key passed as arg
    pickled_object = pickle.dumps(object)
    app.redis.set(key, pickled_object)


def fetch(key):
    # checks redis for picked object at key passed as argument
    # if finds object, unpickles and returns it
    # if no object at given key, returns None
    try:
        unpacked_object = pickle.loads(app.redis.get(key))
        return unpacked_object
    except:
        return None


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
