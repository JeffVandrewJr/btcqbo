from app import db

class QBOTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    realm_id = db.Column(db.String(64))

    def __repr__(self):
        return f"Access: {access_token} \n Refresh: {refresh_token}"

class BTCPTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_token = db.Column(db.String(500))

    def __repr__(self):
        return f"BTCPay Token: {btc_token}"
    
