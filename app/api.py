from app import app
from flask_restful import Resource, Api
from flask import request
from app.qbo import post_payment

api = Api(app)

class PostPayment(Resource):
    def post(self):
        json_data = request.get_json()
        dict = json_data.JSONDecoder()
        try:
            inv_id = dict['id']
        except:
            return #TODO Log an error
        btc_client = fetch('btc_client')
        invoice = btc_client.get_invoice(inv_id)
        try:
            if invoice['status'] == "complete":
                paid = True
        except:
            return
        if paid == true:
            try:
                doc_number = invoice['orderId']
            except:
                return
            try:
                amount_paid = invoice['price']
            except:
                return
            amount = float(amount_paid)
            if amount > 0 and doc_number != None:
                post_payment(doc_number=str(doc_number), amount=amount)
        
