import os

class Config(object):
    SECRET_KEY = os_environ.get('SECRET_KEY') or 'lkjvasdfjkhvasjkhvsdlkvlksdvnjksdnvjngbkmdhjvnlkdjkkflg'
