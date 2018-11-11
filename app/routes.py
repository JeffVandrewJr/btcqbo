import os
from flask import render_template
from app import app
from quickbooks import Oauth2SessionManager 

callback_url = 'http://localhost:5000'

@app.route('/auth')
def auth():
    session_manager = Oauth2SessionManager(
        client_id = os.environ['QUICKBOOKS_CLIENT_ID'],
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        base_url = callback_url,
    )
    authorize_url = session_manager.get_authorize_url(callback_url)
    session_manager.get_access_tokens(request.GET['code'])
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token

@app.route('/')
@app.route('/index')
def index():
    return "Hello World"
