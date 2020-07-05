from app import app
from flask_sqlalchemy import SQLAlchemy
from flask import session
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate(app, db)



# create a users table
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False) 
    super_user = db.Column(db.Boolean)
    email = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(30), nullable=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    last_seen = db.Column(db.DateTime)
    date_created = db.Column(db.DateTime, default=datetime.now)
    wallet = db.relationship("Wallet", backref="user", lazy=True, uselist=False)
    
    # password is to be restricted to only staffs

    def isAuthenticated(self):
        return "email" in session and User.query.filter_by(email=session["email"]).first()

    def user(self):
        if self.isAuthenticated():
            
            return User.query.filter_by(email=session["email"]).first()
        else:
            return "Anonymous"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id":self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)
    def __str__(self):
        return f"{self.last_name.capitalize()} {self.first_name.capitalize()}"

class Wallet(db.Model):
    __tablename__ = "wallet"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    btc_address = db.Column(db.String(255), nullable=False, default=" ")
    eth_address = db.Column(db.String(255), nullable=False, default=" ")
    litecoin_address = db.Column(db.String(255), nullable=False, default=" ")
    bch_address = db.Column(db.String(255), nullable=False, default=" ")
    transaction = db.relationship("Transaction", backref="wallet", lazy=True)
    deposit = db.relationship("Deposit", backref="wallet", lazy=True)
    withdraw = db.relationship("Withdraw", backref="wallet", lazy=True)
    currency_id = db.Column(db.Integer, db.ForeignKey("cryptocurrency.id"))

    def __str__(self):
        return f"<Wallet {self.user.username} >"
    

class CryptoCurrency(db.Model):
    __tablename__ = "cryptocurrency"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(8), nullable=False)
    wallet = db.relationship("Wallet", backref="cryptocurrency", lazy=True)
    displayDeposit = db.relationship("DisplayDeposit", backref="cryptocurrency", lazy=True)
    displayWithdrawal = db.relationship("DisplayWithdrawal", backref="cryptocurrency", lazy=True)
    image_url = db.Column(db.String(100), nullable=False)
    # plan = db.relationship("SubscriptionPlan", backref="cryptocurrency", lazy=True)
    address = db.Column(db.String(255), nullable=False, default=" ")

    def __str__(self):
        return f"<CryptoCurrency {self.code} >"





class SubscriptionPlan(db.Model):
    __tablename__ = "subscription_plan"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    deposit = db.relationship("Deposit", backref="plan", lazy=True)
    time_period = db.Column(db.Integer, nullable=False)
    # plan = db.relationship("Plan", backref="subscription", lazy=True)
    description = db.Column(db.String(255), nullable=False)
    min_depositable = db.Column(db.String, nullable=False) #change al price and perentage columns to float fields
    max_depositable = db.Column(db.String, nullable=False)
    percentage_bonus = db.Column(db.String, nullable=False)
    # cryptocurrency = db.Column(db.Integer, db.ForeignKey("cryptocurrency.id"), nullable=False)


    def __str__(self):
        return f"<SubscriptionPlan {self.name} >"

# class Plan(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     subscription_plan_id = db.Column(db.Integer, db.ForeignKey("subscription_plan.id"), nullable=False)
#     min_depositable = db.Column(db.String, nullable=False) #change al price and perentage columns to float fields
#     max_depositable = db.Column(db.String, nullable=False)
#     percentage_bonus = db.Column(db.String, nullable=False)
    
    

class FAQ(db.Model):
    __tablename__ = "faq"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable =False)
    url = db.Column(db.String(70))


class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable =False)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable =False)


class Slider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_title = db.Column(db.Text, nullable = True)
    title = db.Column(db.Text, nullable = False)
    description = db.Column(db.Text, nullable = False)


class SiteDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(125), nullable=False)
    phone = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    site = db.Column(db.String(50), nullable=False)




class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    subject = db.Column(db.String)
    message = db.Column(db.Text, nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_time = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float, default=0.0, nullable=False)
    deposit = db.relationship("Deposit", backref="transaction", lazy=True, uselist=False)
    withdrawal = db.relationship("Withdraw", backref="transaction", lazy=True, uselist=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    proof = db.Column(db.String(125), nullable=True, default="")
    is_successful = db.Column(db.Boolean, nullable=False, default=False)
    is_deposit = db.Column(db.Boolean, nullable=False, default=False)
    is_withdrawal = db.Column(db.Boolean, nullable=False, default=False)

    def __call__(self):
        if self.is_deposit:
            deposit = Deposit(amount=self.amount, transaction=self)
            db.session.add(deposit)
        elif self.is_withdrawal:
            withdrawal = Deposit(amount=abs(self.amount), transaction=self)
            db.session.add(withdrawal)
    
    def balance(self):
        return sum([ t.amount for t in Transaction.query.filter_by(wallet=User().user().wallet).all() if t.is_successful])



class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deposit_time = db.Column(db.DateTime, default=datetime.now)
    time_approved = db.Column(db.DateTime)
    amount = db.Column(db.Float, default=0.0, nullable=False)
    is_successful = db.Column(db.Boolean, nullable=False, default=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transaction.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("subscription_plan.id"), nullable=False, default=1)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False, default=0)
    proof = db.Column(db.String(125), nullable=True)
    
    def total(self):
        return sum([ t.amount for t in Deposit.querry.all()])


# Withdrawal and deposit should have access to wallet, deposit should have access to proof 
class Withdraw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, default=0.0, nullable=False)
    withdrawal_time = db.Column(db.DateTime, default=datetime.now)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transaction.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    is_successful = db.Column(db.Boolean, nullable=False, default=False)
    time_approved = db.Column(db.DateTime)

    def total(self):
        return sum([ t.amount for t in Withdraw.querry.all()])



class DisplayDeposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.String(20), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey("cryptocurrency.id"), nullable=False)

class DisplayWithdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.String(20), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey("cryptocurrency.id"), nullable=False)


