import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lkjvasdfjkhvasjkhvsdlkvlksdvnjksdnvjngbkmdhjvnlkdjkkflg'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
