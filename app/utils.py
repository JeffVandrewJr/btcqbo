import pickle
import requests
import os
from urllib.parse import urljoin
from app import app


def save(key, object):
    pickled_object = pickle.dumps(object)
    app.redis.set(key, pickled_object)


def fetch(key):
    try:
        unpacked_object = pickle.loads(app.redis.get(key))
        return unpacked_object
    except:
        return None


def wipe(key):
    app.redis.delete(key)


def login(cookies):
    url = urljoin(str(os.getenv('BTCPAY_HOST')), 'api-tokens')
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
