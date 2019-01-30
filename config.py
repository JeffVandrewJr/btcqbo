from apscheduler.jobstores.redis import RedisJobStore
from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    BTCPAY_HOST = os.environ.get('BTCPAY_HOST')
    CALLBACK_URL = os.environ.get('CALLBACK_URL')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    SECRET_KEY = '00000000000'
    SCHEDULER_JOBSTORES = {
            'default': RedisJobStore(host=REDIS_HOST)
        }
