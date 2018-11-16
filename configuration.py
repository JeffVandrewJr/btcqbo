import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lkjvasdfjkhvasjkhvsdlkvlksdvnjksdnvjngbkmdhjvnlkdjkkflg'
    CLIENT_ID = os.environ['QUICKBOOKS_CLIENT_ID'],
    CLIENT_SECRET = os.environ['QUICKBOOKS_CLIENT_SECRET'],

