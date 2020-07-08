from app import app
from flask import render_template, url_for, request, jsonify, redirect, url_for, make_response, flash, send_from_directory, abort, Markup
from werkzeug.utils import secure_filename 
from datetime import datetime
from models.models import *
import os
from helpers.imageHandler import imageHandler
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FileField, PasswordField, HiddenField, IntegerField, DateTimeField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email
from helpers.imageHandler import allowed_image, imageHandler
import imghdr

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        
        if not User().isAuthenticated() :
           
            return abort(404)
        elif User().isAuthenticated() and not User().user().super_user:
            return abort(404)

        return self.render('admin/index.html')

admin = Admin(app, index_view=MyAdminIndexView())


def pic_validation(form, field):
        if field.data:
            filename = field.data.filename
            if not allowed_image(filename):
                raise ValidationError("Invalid file for the specific type")
            return True
        raise ValidationError("No file found")

            

class CryptoCurrencyForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    code = StringField("Code", validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField("CryptoCurrency Address", validators=[DataRequired()])
    # email = StringField("Email", validators=[DataRequired(), Email()])
    image = FileField("CryptoCurrency Image", validators=[DataRequired(), pic_validation])
    image_url = HiddenField("")
    # password = PasswordField("Password", validators=[DataRequired(), Length(min=2, max=20)])


class SubscriptionPlanForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    time_period = IntegerField("Time Period (in days)", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired(), Length(min=2)])

def wallet_query():
    return Wallet.query

class TransactionForm(FlaskForm):
    amount = StringField("Amount")
    transaction_time = DateTimeField("Transaction Time")
    is_successful = BooleanField("Is Successful")
    is_deposit = BooleanField("Is Deposit")
    is_withdrawal = BooleanField("Is Withdrawal")
    wallet = QuerySelectField(query_factory=wallet_query, allow_blank=False)
    proof = StringField("Proof")


def user_query():
    return User.query

def crypto_query():
    return CryptoCurrency.query


# class WalletForm(FlaskForm):
#     plan = QuerySelectField(query_factory=plan_query, allow_blank=False)
#     user = QuerySelectField(query_factory=user_query, allow_blank=False)
#     cryptocurrency = QuerySelectField(query_factory=crypto_query, allow_blank=False) 

    
@app.route("/uploads/<path:filename>")
def get_upload(filename):
    try:
        return send_from_directory(app.config["UPLOADS"], filename= filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)



class ControlerView(ModelView):
    
    def is_accessible(self):
        # if User.query.all()
        return User().isAuthenticated() and User().user().super_user
        # else:
        #     return User().isAuthenticated()
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return abort(404)

    # def _handle_view(self, name):
    #     print("===========================")
    #     if not self.is_accessible():
    #         return redirect(url_for('login'))



class SubscriptionPlanView(ControlerView):
    form_excluded_columns = ('wallet', "deposit")


def _currency_image_formatter(view, context, model, name):
        if model.image_url:
            markupstring = f"<a href='{url_for('get_upload', filename=model.image_url)}'>{url_for('get_upload', filename=model.image_url)}</a>"
            return Markup(markupstring)
        else:
            return ""


class CryptoCurrencyView(ControlerView):
    form = CryptoCurrencyForm

    column_formatters = {
        "image_url": _currency_image_formatter
    }



    def update_model(self, form, model):
        """
            Update model from the form.

            Returns `True` if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
            :param model:
                Model instance
        """

        if form.data and form.validate:
            model.name = form.name.data.capitalize()
            model.code = form.code.data.upper()
            model.address = form.address.data
            model.image_url = imageHandler(form.image.data)
            self.session.commit()
            return True
        return False



    def create_model(self, form):
        """
            Create model from the form.

            Returns the model instance if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
        """

        if form.data:
            model = self.model()
            model.name = form.name.data.capitalize()
            model.code = form.code.data.upper()
            model.address = form.address.data
            model.image_url = imageHandler(form.image.data)
            self.session.add(model)
            self.session.commit()
            return self.model


def _proof_formatter(view, context, model, name):
        if model.proof:
            markupstring = f"<a href='{url_for('get_upload', filename=model.proof)}'>{url_for('get_upload', filename=model.proof)}</a>"
            return Markup(markupstring)
        else:
            return ""


class WalletView(ControlerView):
    form_excluded_columns = ("transaction")
    

class TransactionView(ControlerView):

    can_create = False
    can_edit = False
    # form = TransactionForm
    form_excluded_columns = ("deposit", "withdrawal")
    
    column_formatters = {
        "proof": _proof_formatter
    }

    # @expose('/new/', methods=['GET'])
    # def create_view(self):
    #     # render your view here

    #     return self.render("admin/transaction_create.html")
    
    def update_model(self, form, model):
        """
            Update model from the form.

            Returns `True` if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
            :param model:
                Model instance
        """
        # print("model =============== ", form.amount)
        if form.data and form.validate:
            
            model.wallet = form.wallet.data
            if form.is_withdrawal.data:
                model.amount = -float(form.amount.data)
                model.is_withdrawal = form.is_withdrawal.data
                model.is_deposit = False 
            elif form.is_deposit.data:
                model.amount = form.amount.data
                model.is_withdrawal = False
                model.is_deposit = form.is_deposit.data  
            else:
                model.is_withdrawal = False
                model.is_deposit = False   
                flash("Please select the type of transaction to continue","warning")
                return False
            model.proof = form.proof.data
            
            # if form.is_successful.data:
            #     model.deposit.successful_tine = datetime.now
            if not model.is_successful and form.is_successful.data:
                model.is_successful = form.is_successful.data
                model.transaction_time = form.transaction_time.data
            else:
                flash("Transaction has already been successful","warning")

            if model.is_deposit:
                deposit = Deposit.query.filter_by(transaction=model)
                deposit.amount=model.amount
                if model.is_successful:
                    deposit.time_approved = datetime.now()
                    deposit.is_successful = model.is_successful
                deposit.wallet = model.wallet
                deposit.proof = model.proof
                deposit.plan = model.plan
            elif model.is_withdrawal:
                if float(form.amount.data) <= sum([t.amount for t in Transaction.query.filter_by(wallet=form.wallet.data) if t.is_successful]):
                    withdrawal = Withdraw.query.filter_by(transaction=model, wallet=model.wallet)
                    withdrawal.amount=abs(model.amount)
                    
                    if model.is_successful:
                        
                        withdrawal.is_successful = model.is_successful
                        withdrawal.time_approved = datetime.now()
                        print("withdrawal.is_successful ============", withdrawal.is_successful, withdrawal.time_approved)
                        return False
                else:
                    flash("User balance is not up to that amount","warning")
                    return False
    
            self.session.commit()
            return True
        return False

    
    def delete_model(self, model):
        """
            Delete model.
            :param model:
                Model to delete
        """
        try:
            if model.is_deposit:
                db.session.delete(model.deposit)
            elif model.is_withdrawal:
                db.session.delete(model.withdrawal)
            db.session.delete(model)
            db.session.commit()
            
            # Add your custom logic here and don't forget to commit any changes e.g. 
            # self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to delete record.')

            self.session.rollback()

            return False
        else:
            self.after_model_delete(model)

        return True

    def create_model(self, form):
        """
            Create model from the form.

            Returns the model instance if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
        """
        print( self.model)
        if form.data and form.validate:
            model = self.model()
            
            model.wallet = form.wallet.data
            if form.is_withdrawal.data:
                if float(form.amount.data) <= sum([t.amount for t in Transaction.query.filter_by(wallet=form.wallet.data) if t.is_successful]):
                    model.amount = -abs(float(form.amount.data))
                    model.is_withdrawal = form.is_withdrawal.data
                    model.is_deposit = False 
                else:
                    flash("User balance is not up to that amount","warning")
                    return False
            elif form.is_deposit.data:
            
                model.amount = form.amount.data
                model.is_withdrawal = False
                model.is_deposit = form.is_deposit.data
                
            else:     
                model.is_withdrawal = False
                model.is_deposit = False
                flash("Please select the type of transaction to continue","warning")
                return False
                
            model.proof = form.proof.data
            model.is_successful = form.is_successful.data
            model.transaction_time = form.transaction_time.data

            self.session.add(model)

            if model.is_deposit:
                deposit = Deposit(amount=model.amount, transaction=model)
                deposit.is_successful = model.is_successful
                deposit.wallet = model.wallet
                deposit.proof = model.proof
                print("hello")
                if model.is_successful:
                    deposit.time_approved = datetime.now()
                self.session.add(deposit)
                self.session.commit()
                return "Hello"
                return redirect(f"/admin/deposit/edit/?id={deposit.id}")
                
                
                try:
                    deposit.plan = model.plan
                except:
                    flash(f"Please to add deposit follow this <a href='/admin/deposit'>link</a>")
                    return False
                
            elif model.is_withdrawal:
                withdrawal = Withdraw(amount=abs(model.amount), transaction=model, wallet=model.wallet)
                if model.is_successful:
                        withdrawal.is_successful = model.is_successful
                        withdrawal.time_approved = datetime.now()
                self.session.add(withdrawal)
                self.session.commit()
                return redirect(f"/admin/withdraw/edit/?id={withdrawal.id}")
                
                self.session.add(withdrawal)


            self.session.commit()
  
            return self.model

class DepositView(ControlerView):
    form_edit_rules = []
    column_formatters = {
        "proof": _proof_formatter
    }
    form_excluded_columns = ("time_approved","transaction")

    def delete_model(self, model):
        """
            Delete model.
            :param model:
                Model to delete
        """
        try:
            
            db.session.delete(model.transaction)
            db.session.delete(model)
            db.session.commit()
            
            # Add your custom logic here and don't forget to commit any changes e.g. 
            # self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to delete record.')

            self.session.rollback()

            return False
        else:
            self.after_model_delete(model)

        return True


    def update_model(self, form, model):
        """
            Update model from the form.

            Returns `True` if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
            :param model:
                Model instance
        """
        # print("model =============== ", form.amount)
        if form.data and form.validate:
            model.transaction.wallet = form.wallet.data
            model.transaction.amount = float(form.amount.data)
            model.transaction.is_deposit = True
            if not model.is_successful and form.is_successful.data:
                model.time_approved = datetime.now()

                model.transaction.is_successful = True
                model.is_successful = True
            elif model.is_successful and form.is_successful.data:
                flash("Deposit has already been successful","warning")
            
            model.wallet = form.wallet.data
            model.amount = float(form.amount.data)

            model.proof = form.proof.data
            print("Proof ====", form.proof.data)
            model.transaction.proof = form.proof.data
            
           
            model.transaction.transaction_time = datetime.now()

    

            self.session.commit()
            return True
        return False



    def create_model(self, form):
        """
            Create model from the form.

            Returns the model instance if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
        """
        print( self.model)
        if form.data and form.validate:
            model = self.model()
            transaction = Transaction()
            model.transaction = transaction
            transaction.wallet = form.wallet.data
            model.wallet = form.wallet.data
        
            model.amount = float(form.amount.data)
            transaction.amount = float(form.amount.data)
            transaction.is_withdrawal = False
            transaction.is_deposit = True
            if not model.is_successful and form.is_successful.data:
                transaction.is_successful = True
                model.is_successful = True
                model.time_approved = datetime.now()

            model.is_withdrawal = False
  
            model.proof = form.proof.data
            transaction.prrof = form.proof.data
            model.is_successful = form.is_successful.data
            transaction.transaction_time = datetime.now()

            self.session.add(model)
            self.session.add(transaction)        

            
            self.session.commit()
  
            return self.model

class WithdrawView(ControlerView):
    form_edit_rules = []

    form_excluded_columns = ("transaction")

    def delete_model(self, model):
        """
            Delete model.
            :param model:
                Model to delete
        """
        try:
            
            db.session.delete(model.transaction)
            db.session.delete(model)
            db.session.commit()
            
            # Add your custom logic here and don't forget to commit any changes e.g. 
            # self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to delete record.')

            self.session.rollback()

            return False
        else:
            self.after_model_delete(model)

        return True


    def update_model(self, form, model):
        """
            Update model from the form.

            Returns `True` if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
            :param model:
                Model instance
        """
        # print("model =============== ", form.amount)
        if form.data and form.validate:
            model.transaction.wallet = form.wallet.data
            model.wallet = form.wallet.data
            if float(form.amount.data) <= sum([t.amount for t in Transaction.query.filter_by(wallet=form.wallet.data) if t.is_successful]): 
                model.transaction.amount = -abs(float(form.amount.data))
                model.amount = abs(float(form.amount.data))
            else:
                flash("User balance is not up to that amount","warning")
                return False
            model.transaction.is_withdrawal = True
            
          
            model.withdrawal_time = datetime.now()

            if form.is_successful.data and not model.is_successful:
                model.is_successful = True
                model.transaction.is_successful = True
                model.time_approved = datetime.now()
            elif form.is_successful.data and mode.is_successful:
                flash("Withdrawal has allready been successful")
                
            
          
                         
            # model.proof = form.proof.data
            
            
           
            model.transaction.transaction_time = datetime.now()

    

            self.session.commit()
            return True
        return False



    def create_model(self, form):
        """
            Create model from the form.

            Returns the model instance if operation succeeded.

            Must be implemented in the child class.

            :param form:
                Form instance
        """
        print( self.model)
        if form.data and form.validate:
            model = self.model()
            transaction = Transaction()
            model.transaction = transaction
            transaction.wallet = form.wallet.data
            model.wallet = form.wallet.data
        
            if float(form.amount.data) <= sum([t.amount for t in Transaction.query.filter_by(wallet=form.wallet.data) if t.is_successful]): 
                model.transaction.amount = -abs(float(form.amount.data))
                model.amount = abs(float(form.amount.data))
            else:
                flash("User balance is not up to that amount","warning")
                return False
            transaction.is_withdrawal = True
    
            if form.is_successful.data:
                transaction.is_successful = True
                model.is_successful = True
                model.time_approved = datetime.now()

            
  
            # model.proof = form.proof.data
            # transaction.prrof = form.proof.data
           
            transaction.transaction_time = datetime.now()

            self.session.add(model)
            self.session.add(transaction)        

            
            self.session.commit()
  
            return self.model



admin.add_view(ControlerView(User, db.session))

admin.add_view(ControlerView(Slider, db.session))

admin.add_view(WalletView(Wallet, db.session))

admin.add_view(CryptoCurrencyView(CryptoCurrency, db.session))

admin.add_view(SubscriptionPlanView(SubscriptionPlan, db.session))

# admin.add_view(ControlerView(Plan, db.session))

admin.add_view(ControlerView(FAQ, db.session))

admin.add_view(ControlerView(SiteDetails, db.session))

admin.add_view(ControlerView(ContactUs, db.session))

admin.add_view(TransactionView(Transaction, db.session))

admin.add_view(DepositView(Deposit, db.session))

admin.add_view(WithdrawView(Withdraw, db.session))

admin.add_view(ControlerView(DisplayDeposit, db.session))

admin.add_view(ControlerView(DisplayWithdrawal, db.session))

## NOTE, USERS WITHOUT ADMIN PRIVILAGES ARE NOT ALLOWED TO USE THESE ADMIN ROUTES
## Edit the delete routes to allow GET requests but returns 404 in get but allows POST requests to go through

    
                

                
                
           
