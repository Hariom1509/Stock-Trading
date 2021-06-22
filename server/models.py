from datetime import datetime, timezone
from server import db, login_manager
from flask_login import UserMixin


@ login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))	

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), unique = True, nullable = False)
	email = db.Column(db.String(120), unique = True, nullable = False)
	image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
	password = db.Column(db.String(60), nullable = False)
	account = db.relationship('Account', lazy=True)
	assets = db.relationship('Assets', lazy=True)
	transaction_history = db.relationship('Transaction_History',  lazy = True)
	fav = db.relationship('Fav_Stock', lazy=True)
	def __repr__(self):
		return f"User('{self.username}','{self.email}', '{self.image_file}')"

class Account(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	money = db.Column(db.Float,default = 100000)
	asset_value = db.Column(db.Float)
	total = db.Column(db.Float)
	commission_type = db.Column(db.Boolean, default = True,  nullable = False)
	commission = db.Column(db.Float, default = 1)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)

	def __repr__(self):
		return f"Account('{self.money}','{self.asset_value}', '{self.total}' ,'{self.commission_type}', '{self.commission}' , '{self.user_id}')"

class Assets(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	stock = db.Column(db.String(3), nullable = False)
	quantity = db.Column(db.Integer, nullable = False)
	price = db.Column(db.Float, default = 0)
	value = db.Column(db.Float, default = 0)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)

	def __repr__(self):
		return f"Assets('{self.stock}','{self.quantity}','{self.price}','{self.value}','{self.user_id}')"

class Transaction_History(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	stock = db.Column(db.String(4), nullable = False)
	position = db.Column(db.Boolean, nullable = False)
	price = db.Column(db.Float, nullable = False)
	quantity = db.Column(db.Integer, nullable = False)
	commission_type = db.Column(db.Boolean)
	commission = db.Column(db.Float,nullable = False)
	total = db.Column(db.Float,nullable = False)
	time = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)

	def __repr__(self):
		return f"Transaction_History('{self.stock}', '{self.position}' ,'{self.price}','{self.quantity}', '{self.commission_type}','{self.commission}' , '{self.time}', '{self.user_id}')"

class Fav_Stock(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	stock_code = db.Column(db.String(4))
	stock_code1 = db.Column(db.String(4))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)
	def __repr__(self):
		return f"Fav_Stock('{self.stock_code}','{self.stock_code1}','{self.user_id}')"


