import os
from flask import render_template, redirect, request
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
    return redirect(authorize_url)

@app.route('/')
@app.route('/index')
def index():
    session_manager = Oauth2SessionManager(
        client_id = os.environ['QUICKBOOKS_CLIENT_ID'],
        client_secret = os.environ['QUICKBOOKS_CLIENT_SECRET'],
        base_url = callback_url,
    )
    code = request.args.get('code') #this is a flask thing for pulling query string arguments from the URL route
    session_manager.get_access_tokens(code)
    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
    return str(access_token) + "  |  " + str(refresh_token)
