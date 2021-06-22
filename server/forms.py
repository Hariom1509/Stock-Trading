from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo,InputRequired,ValidationError
from server.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
	username = StringField('Username',validators = [DataRequired(), Length(min = 2, max = 32)])
	email = StringField("Email",  validators=[DataRequired(), Email()])
	password = PasswordField('Password' ,  validators = [DataRequired()])
	confirm_password = PasswordField('confirm_password' , validators = [DataRequired(), EqualTo('password',"Passwords must match")])
	signup = SubmitField('Sign up')

	def validate_username(self, username):
		user_new = User.query.filter_by(username = username.data).first()
		if user_new:
			raise ValidationError('That username has been taken. Please choose another one')

	def validate_email(self, email):
		email_new = User.query.filter_by(email = email.data).first()
		if email_new:
			raise ValidationError('That email has been taken. Please choose another one')


class LoginForm(FlaskForm):
	email = StringField('Email' , validators = [DataRequired(), Email() ])
	password = PasswordField('Password' ,  validators = [DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

class UpdateForm(FlaskForm):
	username = StringField('Username',validators = [DataRequired(), Length(min = 2, max = 32)])
	email = StringField("Email",  validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	update = SubmitField('Update')
		

	def validate_username(self, username):
		if username.data != current_user.username:
			user_new = User.query.filter_by(username = username.data).first()
			if user_new:
				raise ValidationError('That username has been taken. Please choose another one')

	def validate_email(self, email):
		if email.data != current_user.email:
			email_new = User.query.filter_by(email = email.data).first()
			if email_new:
				raise ValidationError('That email has been taken. Please choose another one')

# 1 is percentage and 0 fixed

class CommissionForm(FlaskForm):
	commission_type_p = BooleanField('Percentage Checked')
	commission_type_f = BooleanField('Fixed Checked')
	fixed = FloatField('Fixed', validators = [InputRequired()])
	percentage = FloatField('Percentage', validators = [InputRequired()])
	update = SubmitField('Update Commission Status')

class AccountForm(FlaskForm):
	money = FloatField('Cash',validators = [DataRequired()])
	update1 = SubmitField('Update your Account')


class BuySellForm(FlaskForm):
	stock = StringField('Stock', validators = [DataRequired(), Length(min = 2, max = 5)])
	position = BooleanField('Position')
	quantity = IntegerField('Quantity', validators = [DataRequired()])
	price = FloatField('Cash',validators = [DataRequired()])
	buy = SubmitField('Buy')
	sell = SubmitField('Sell')

class StockForm(FlaskForm):
	stock = StringField('Stock')
	search = SubmitField('Search')
	add_favourite = BooleanField('Add to Favourites')

