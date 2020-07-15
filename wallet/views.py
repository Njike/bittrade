from app import app

from flask import Flask, render_template, jsonify, url_for, request, jsonify, redirect, url_for, make_response, flash, send_from_directory, abort, session

from models.models import *
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FileField, PasswordField, HiddenField, IntegerField, SubmitField, TextField
from wtforms.validators import DataRequired, Length, Email, EqualTo, email_validator, ValidationError
from wtforms.widgets import TextArea
from wtforms_sqlalchemy.fields import QuerySelectField
from passlib.hash import sha256_crypt
from functools import wraps
from helpers.imageHandler import imageHandler, allowed_image
from helpers.general import exchange_rate, send_reset_email
import json
import requests

class SupportForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired(), Length(min=2)])
    email = StringField("Your Email", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=2)])
    message = StringField("Message", widget=TextArea(),  validators=[DataRequired(), Length(min=2)])

class RegistratonForm(FlaskForm):
    firstname = StringField("First Name", validators=[DataRequired(), Length(min=2)])
    lastname = StringField("Last Name", validators=[DataRequired(), Length(min=2)])
    username = StringField("Userame", validators=[DataRequired(), Length(min=2)])
    password1 = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8), EqualTo("password1", message='Passwords must match')])
    email = StringField("Email", validators=[DataRequired(), Email()])
    agree = BooleanField(validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("User already exist")
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exist, please choose a different one")



class AccountForm(FlaskForm):
    username = StringField("Username")
    firstname = StringField("Firstname", validators=[DataRequired(), Length(min=2)])
    lastname = StringField("Lastname", validators=[DataRequired(), Length(min=2)])
    email = StringField("Email")
    btc_address = StringField("Bitcoin Address")
    eth_address = StringField("Ethereum Address")
    litecoin_address = StringField("Litecoin Address")
    bch_address = StringField("Bitcoin Cash Address")
    current_password = PasswordField("Current Password", validators=[])
    new_password = PasswordField("New Password")
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("new_password", message='Passwords must match')])

    def validate_current_password(self, password):
        user = User().user()
        print(password.data)
        if password.data and not sha256_crypt.verify(password.data, user.password):
            raise ValidationError("Invalid password, please input the correct passowrd")

    # def validate_new_password(self, password):
    #     if not self.current_password.data:
    #         flash("Please input your current password", "warning")
    #         return ValidationError("Please input your current password")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Invalid email address")


class RequestRegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    

class PasswordResetForm(FlaskForm):
    password1 = PasswordField("New Password", validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8), EqualTo("password1", message='Passwords must match')])
   






class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    remember = BooleanField("Remember me")

    def validate_email(self, email):
       
        email_validator.validate_email(
                    email.data.strip(),
                    check_deliverability=False,
                    allow_smtputf8=True,
                    allow_empty_local=False,
                )   

    # def validate_password(self, password):
    #     user = User.query.filter_by(email=self.email.data).first()
    #     if user:
    #         if not sha256_crypt.verify(password.data, user.password):
    #             raise ValidationError("Invalid email address or password")

class DepositForm(FlaskForm):
    super(FlaskForm)
    pass



@app.context_processor
def g():
    site_detail = SiteDetails.query.first()
    user=User().user()
    if type(User().user()) == str:
        return {"current_user":None, "site_detail":site_detail, "date":datetime.now()}
    detail = {"deposits":[],"withdrawals":[],"pendingWithdrawals":[], "pendingDeposits":[]}
    transactions = Transaction.query.filter_by(wallet=user.wallet).all()
    for transaction in transactions:
        if transaction.is_deposit and transaction.is_successful:
            detail["deposits"].append(transaction.deposit.amount)
        elif transaction.is_withdrawal and transaction.is_successful:
            detail["withdrawals"].append(abs(transaction.withdrawal.amount))
        elif transaction.is_withdrawal and not transaction.is_successful:
            detail["pendingWithdrawals"].append(abs(transaction.withdrawal.amount))
        elif transaction.is_deposit and not transaction.is_successful:
            detail["pendingDeposits"].append(transaction.deposit.amount)


    
    return {"detail":detail,"site_detail":site_detail, "current_user":User().user(), "balance":round(Transaction.query.filter_by(wallet=User().user().wallet).first().balance(),6), "date":datetime.now()
}


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if User().isAuthenticated():
            return f(*args, **kwargs)
        else:
            # print(str(f).split(' ')[1], "=================")
            # flash("Unauthorized, Please login", "warning")
            n = str(f).split(' ')[1]
            if n == "logout":
                return redirect(url_for("login"))
            return redirect(url_for("login", next=n))
    return wrap


def create_transaction(amount, wallet, is_deposit=False, proof="", is_withdrawal=False, is_successful=False, plan=None):
    transac = Transaction(is_successful=is_successful,amount=amount, is_deposit=is_deposit,\
                     is_withdrawal=is_withdrawal, wallet=wallet, proof=proof)
    db.session.add(transac)

    if transac.is_deposit and transac.is_withdrawal:
        deposit = Deposit(amount=amount, transaction=transac, proof=proof, wallet=wallet, is_successful=is_successful)
        db.session.add(deposit)
        withdrawal = Withdraw(amount=-amount, transaction=transac, wallet=wallet)
        db.session.add(withdrawal)

    elif transac.is_deposit:
        if not plan:
            flash("Please select a plan", "warning")
            return redirect(request.url)
        deposit = Deposit(amount=amount, transaction=transac, plan=plan)
        deposit.proof = proof
        deposit.wallet = wallet
        # if is_successful:
        #     deposit.is_successful = True
        #     deposit.time_approved = datetime.now()
        db.session.add(deposit)
    elif transac.is_withdrawal:
        withdrawal = Withdraw(amount=-amount, transaction=transac, wallet=wallet)

        db.session.add(withdrawal)
    
    db.session.commit()

def update_transaction(amount, proof, wallet, is_deposit=False, is_withdrawal=False):
    transac = Transaction.query.filter_by(wallet=wallet)
    transac.amount = amount
    
    if transac.is_deposit:
        deposit = Deposit.query.filter_by(transaction=transac)
        deposit.amount=amount
    
    elif transac.is_withdrawal:
        withdrawal = Withdraw.query.filter_by(transaction=transac)
        withdrawal.amount=-amount
    db.session.commit()

@app.route("/")
def index():
    sliders = Slider.query.all()
    deposits = DisplayDeposit.query.all()
    withdrawals = DisplayWithdrawal.query.all()
    

    plans = SubscriptionPlan.query.all()

    return render_template('index.html', sliders=sliders, deposits=deposits, withdrawals=withdrawals, plans=plans)


@login_required
@app.route("/data/", methods=["GET"])
def update():
    user = User().user()
    transac = Transaction.query.filter_by(wallet=user.wallet).first()
    

    toReturn = {"balance":transac.balance(),
                 "currency":user.wallet.cryptocurrency.code, 
                 }
    return jsonify(toReturn)

@app.route("/sitemap.xml")
def map():
    try:
        return send_from_directory("../static", filename="sitemap.xml", as_attachment=False)
    except FileNotFoundError:
        abort(404)

@app.route("/register/", methods=["GET", "POST"])
def verifyEmail():
    form = RequestRegisterForm()

    if User().isAuthenticated():
        return redirect(url_for("index"))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # flash("Invalid email address","warning")
            return redirect(url_for("login"))
        send_register_email(form.email.data)
        flash("A link will be sent sent to your Email","info")
        return redirect(url_for("index"))


    return render_template("forgot-password1.html", form=form)

@app.route("/register/<token>", methods=["GET", "POST"])
def register(token):
    single_user = User.query.all()
    if User().isAuthenticated():
        return redirect(url_for("dashboard"))
    form = RegistratonForm()
    cryptocurrency = CryptoCurrency.query.all()

    
        
    if request.method == "POST":

        if not form.validate_on_submit():
            flash("Please fill in the required fields", "warning")
            return redirect(request.url)
        
    

        user = User()
        user.first_name = form.firstname.data
        user.last_name = form.lastname.data
        user.super_user = False
        user.username = form.username.data
        user.email = form.email.data
        user.password = sha256_crypt.encrypt(str(form.password1.data))
        
        if not single_user:
            user.super_user = True

            wallet = Wallet(user=user)

          
            db.session.add(wallet)
            session["isAuthenticated"] = True
            session["email"] = user.email
            
            db.session.add(user)
            create_transaction(amount=0.0,wallet=wallet,is_deposit=True, is_withdrawal=True, is_successful=True)
            flash("Welcome Admin, please fill up the necessary records", "success")
            return redirect("/admin")
        
      

        wallet = Wallet(user=user)

          
        db.session.add(wallet)
        
        db.session.add(user)
        create_transaction(amount=0.0,wallet=wallet,is_deposit=True, is_withdrawal=True, is_successful=True)

        return redirect(url_for("login"))

    return render_template("register.html",cryptocurrency=cryptocurrency, form=form)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if User().isAuthenticated():
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password_candidate = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(email=email).first()

        if user:
            password = user.password

                           

            if sha256_crypt.verify(password_candidate, password):
                if remember: 
                    session.permanent = True
                session["isAuthenticated"] = True
                session["email"] = email
             
                session["username"] = user.username

                if request.args and request.args["next"]:
                    return redirect(url_for(request.args["next"]))

                return redirect(url_for("dashboard"))
            else:
                error = "Invalid email or password"
                flash(error, "danger")
                render_template("login.html", form=form)
            
        else:

            error = "Invalid email or password"
            flash(error, "danger")
            render_template("login.html",form=form)

        

        
        
    return render_template("login.html", form=form)

@app.route("/logout/")
@login_required
def logout():
    User().user().last_seen = datetime.now()
    db.session.commit()
    session.clear()
    return redirect(url_for("login"))

@app.route("/support/", methods=["GET", "POST"])
def support():
    form = SupportForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            flash("Please fill in the required fields", "warning")
        support_model = ContactUs(name=form.name.data, subject=form.subject.data, email=form.email.data, message=form.message.data)
        db.session.add(support_model)
        db.session.commit()
        flash("Message Sent", "success")
        return redirect(request.url)
        # support = SupportForm()
            
    return render_template("support.html", form=form)

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/faq/")
def faq():
    questions = FAQ.query.all()
    return render_template("faq.html", questions=questions)



@app.route("/terms/")
def terms():
    return render_template("rules.html")


@app.route("/plans/")
def plans():
    plans = SubscriptionPlan.query.all()
    return render_template("plans.html", plans=plans)


@app.route("/news/")
def news():
    return render_template("news.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = RequestResetForm()
    if User().isAuthenticated():
        return redirect(url_for("index"))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("Invalid email address","warning")
            return redirect(request.url)
        send_reset_email(user)
        flash("A link will be sent sent to your Email","info")
        return redirect(url_for("login"))

    return render_template("forgot-password.html", form=form)

@app.route("/password_reset/<string:token>", methods=["GET", "POST"])
def password_reset(token):
    form = PasswordResetForm()
    if User().isAuthenticated():
        return redirect(url_for("index"))

    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token","warning")
        return redirect(url_for("forgot_password"))

    if form.validate_on_submit():
        
        user.password = sha256_crypt.encrypt(str(form.password1.data))
        db.session.commit()
        
        flash("Your password has been changes successfuly","success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", form=form)


@app.route("/dashboard/")
@login_required
def dashboard():

    user = User().user()
    transac = Transaction.query.filter_by(wallet=user.wallet).all()
    deposits = [t.deposit for t in transac if t.is_deposit and t.is_successful and t.deposit.plan]


    delta = datetime.now() - user.date_created
    print("Deposits ============", deposits)

    if deposits:
        bonus = (float(deposits[-1].plan.percentage_bonus)/100 ) * deposits[-1].amount

        if delta.days <= int(deposits[-1].plan.time_period):
            print("Days ===============", delta.days)
            session["bonus"] = bonus
        if session["bonus"] and delta.seconds/(60*60) % 24 == 0:
            create_transaction(amount=session["bonus"], wallet=user.wallet,is_deposit=True,is_successful=True,plan=deposits[-1].plan)
            session["bonus"] == None


 
    
    
    

    return render_template("dashboard.html")

@app.route("/account/", methods=["GET","POST"])
@login_required
def account():
    form = AccountForm()
    user = User().user()

    if form.validate_on_submit():

        user.first_name = form.firstname.data
        user.last_name = form.lastname.data
        # user.wallet.cryptocurrency = form.cryptocurrency.data
        user.wallet.btc_address = form.btc_address.data
        user.wallet.eth_address = form.eth_address.data
        user.wallet.litecoin_address = form.litecoin_address.data
        user.wallet.bch_address = form.bch_address.data
        if form.current_password.data and sha256_crypt.verify(form.current_password.data, user.password):
            if sha256_crypt.verify(form.new_password.data, user.password):
                flash("Choose a new password different from the current password", "warning")
                return redirect("/account/") 
            user.password = sha256_crypt.encrypt(str(form.new_password.data))
        elif form.current_password.data and not sha256_crypt.verify(form.current_password.data, user.password):
            flash("Please correctly input your current password", "warning")
            return redirect(url_for(request.url))
            

        

        db.session.commit()
        flash("Account updated sccessfully", "success")
        if request.args and request.args["next"]:
            return redirect(url_for(request.args["next"]))
        return redirect(request.url)
    elif request.method == "GET":
        form.email.data = user.email
        form.username.data = user.username
        form.firstname.data = user.first_name
        form.lastname.data = user.last_name
        # form.cryptocurrency = user.wallet.cryptocurrency
        form.btc_address.data = user.wallet.btc_address
        form.eth_address.data = user.wallet.eth_address
        form.litecoin_address.data = user.wallet.litecoin_address
        form.bch_address.data = user.wallet.bch_address


    return render_template("account-edit.html", form=form)


@app.route("/deposit/", methods=["GET", "POST"])
@login_required
def deposit():
    user = User().user()
    plans = SubscriptionPlan.query.all()
    currencies = CryptoCurrency.query.all()
    form = DepositForm()
    # create_transaction(amount=300,is_deposit=True, wallet=user.wallet, proof="fuck you")
    transaction = Transaction.query.filter_by(wallet=user.wallet).first().balance()



    if request.method == "POST":
        
        if not request.files["proof"]:
            flash("Please upload the proof of payment to continue","warning")
            return redirect(request.url)
        if request.form and not (int(request.form["h_id"]) and int(request.form["type"])):
            flash(f"Invalid Crypto Currency or Plan, Please contact <a href='{url_for(support)}'>our support page</a> to report any issue", "warning")
            return redirect(request.url)
        
        
        if not float(request.form["amount"]):
            flash("Please input a valid amount","warning")
            return redirect(request.url)
        
        image = request.files["proof"]
        
    
        if not allowed_image(image.filename):
                flash("This image extention not allowed", "warning")
                return redirect(request.url)

        proof = imageHandler(image)
        
        plan = int(request.form["h_id"])
        
        amount = float(request.form["amount"].strip())
        cryptocurrency = int(request.form["type"])
        
        
        plan = SubscriptionPlan.query.get(plan)

        currency = CryptoCurrency.query.get(cryptocurrency)
        user.wallet.cryptocurrency = currency

        rate = exchange_rate(currency.code)
        # print(float(plan.min_depositable)/float(rate))
        if float(plan.min_depositable)/float(rate) >= amount:
            flash("Amount less than the expected amount for this plan", "warning")
            return redirect(request.url)
        
        # user.wallet.plan = plan

        create_transaction(proof=proof, amount=amount, wallet=user.wallet, is_deposit=True,plan=plan)
        flash("Deposit Successful", "success")
        return redirect(url_for("dashboard"))
        

            

    

    return render_template("deposit.html",form=form, plans=plans, currencies=currencies)

@app.route("/deposits/", methods=["GET","POST"])
@login_required
def deposit_history():
    form = FlaskForm()
    user = User().user()
    if request.method == "POST":
        transac = request.form["type"]

        if not transac:
            print()
            return render_template("deposit-history.html", form=form, transac=user.wallet.transaction)
        elif transac == "deposit":
            d = [tran for tran in Deposit.query.filter_by(wallet=user.wallet).all() if tran.plan]
            
            return render_template("deposit-history.html", form=form, deposits=d)
        elif transac == "withdrawal":
            d = [tran for tran in Withdraw.query.filter_by(wallet=user.wallet)]
            return render_template("deposit-history.html", form=form, withdrawals=d)
    return render_template("deposit-history.html", form=form, transac=user.wallet.transaction)

# @app.route("/withdrawals/")
# @login_required
# def withdrawal_history():
#     return render_template("withdraw-history.html")

# @app.route("/earnings/")
# @login_required
# def earnings():
#     return render_template("earnimgs.html")

@app.route("/withdrawal/", methods=["GET","POST"])
@login_required
def withdrawal():
    form = FlaskForm() 
    user = User().user()
    balance = user.wallet.transaction[0].balance()

    if request.method == "POST":

        amount = float(request.form["amount"].strip())
        if user.wallet.cryptocurrency:
            crypto = user.wallet.cryptocurrency
          
            if crypto.code == "BTC" and not user.wallet.btc_address.strip():
                flash(f"Please update your Bitcoin address","warning")
                return redirect(url_for("account", next="withdrawal"))
            elif crypto.code == "ETH" and not user.wallet.eth_address.strip():
                flash(f"Please update your Ethereum address","warning")
                return redirect(url_for("account", next="withdrawal"))
            elif crypto.code == "LTC" and not user.wallet.litecoin_address.strip():
                flash(f"Please update your Litecoin address","warning")
                return redirect(url_for("account", next="withdrawal"))
            elif crypto.code == "BCH" and not user.wallet.bch_address.strip():
                flash(f"Please update your Bitcoin Cash address","warning")
                return redirect(url_for("account", next="withdrawal"))
        else:
            flash("Sorry, you dont have any actiive deposit", "warning")
            return redirect(request.url)
        if amount >= balance:
            flash("You have no funds to withdraw", "warning")
            return redirect(request.url)
        
        elif amount > 0:
            create_transaction(is_withdrawal=True, amount=amount, wallet=user.wallet)
        else:
            flash("Invalid amount please check your balance and input a valid amount", "warning")
            return redirect(request.url)            
    return render_template("withdrawal.html",form=form)

@app.route("/deposit-list/")
@login_required
def deposit_list():
    plans = SubscriptionPlan.query.all()
    return render_template("deposit-list.html", plans=plans)
