import os
from flask import render_template, redirect, request
from app import app
import app.qbo as qbo

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/authqbo')
def authqbo():
    return redirect(qbo.get_auth_url())

@app.route('/qbologged')
def qbologged():
    qbo.set_global_vars(
        realmid=request.args.get('realmId'),
        code=request.args.get('code'),
    )
    return str(qbo.access_token) + "  |  " + str(qbo.refresh_token)
