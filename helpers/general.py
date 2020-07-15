import requests

from flask_mail import Message, Mail
from flask import url_for

mail = Mail()

def exchange_rate(crypto):
    res = requests.get(f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={crypto}&to_currency=USD&apikey=Y60HOLBBWTXXE4V4")
    rate = res.json()['Realtime Currency Exchange Rate']['5. Exchange Rate']
    return float(rate)

def send_reset_email(user):
    token = user.get_reset_token()
    print(token, "=============Token")
    msg = Message("Password Reset Request",  recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for("password_reset", token=token, _external=True)} 

If you did not make this request then simply ignore this email and no changes will be made
"""
   
    mail.send(msg)

def send_register_email(email):
    token = User.get_reset_token()
    print(token, "=============Token")
    msg = Message("Registration",  recipients=[email])
    msg.body = f"""Welcome to Bittradeweb, to continue the registration process kindly click following link below:
{url_for("register", token=token, email=email, _external=True)} 

If you did not make this request then simply ignore this email and no changes will be made
"""
   
    mail.send(msg)