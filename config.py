import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    BTCPAY_HOST = os.environ.get('BTCPAY_HOST')
    CALLBACK_URL = os.environ.get('CALLBACK_URL')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    SECRET_KEY = '00000000000'
