import secrets
from datetime import datetime, timezone
import requests
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from server.forms import LoginForm, RegistrationForm, UpdateForm, AccountForm, BuySellForm, StockForm, CommissionForm
from server.models import User, Account, Assets, Transaction_History, Fav_Stock
from server import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
	if current_user.is_authenticated:
		return redirect(url_for('account'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user,remember= form.remember.data)
			return redirect(url_for('account'))
		else:
			flash('You have unsuccessfully logined in, Please try again', 'danger')
	return render_template('home.html', form = form)



#for the position, 1 is buy 0 is sell

@app.route("/trades/buy", methods = ['GET', 'POST'])
@login_required
def trades_buy():
	form = BuySellForm()
	#databases
	fav = Fav_Stock.query.filter_by(user_id = current_user.id).first()
	account = Account.query.filter_by(user_id = current_user.id).first()
	asset = Assets.query.filter_by(user_id = current_user.id)
	user1 = User.query.filter_by(username = current_user.username).first()
	#for the tables
	rounded_stock_value = {}
	url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey=demo=MD4DGMJPV06DEGG1'
	total_stock_value = 0
	for stocks in asset:
		r = requests.get(url.format(stocks.stock.upper())).json()
		r = r['Global Quote']['05. price']
		stocks.price = r
		stocks.total = float(stocks.price) * float(stocks.quantity)
		rounded_stock_value[stocks.stock.upper()] = round(stocks.total,2)
		db.session.commit()
		total_stock_value += float(stocks.total)
	rounded_account = [round(account.money,2), round(account.asset_value,2), round(account.total, 2)]
	print(fav)
	print(User.query.all())
	print(Account.query.all())
	print(Assets.query.all())
	print(Transaction_History.query.all())
	if form.validate_on_submit():
		print(form.stock)
		stock_valuation = form.price.data * form.quantity.data
		if account.commission_type == True:
			commission_stock = stock_valuation * account.commission/100
		else:
			commission_stock = account.commission
		stock_valuation_commission = stock_valuation + commission_stock
		if stock_valuation_commission>account.money:
			flash('You do not have the money to finance this trade', 'danger')
			return redirect(url_for('trades_buy'))
		if Assets.query.filter_by(stock = form.stock.data.upper(), user_id = user1.id).first():
			asset = Assets.query.filter_by(stock = form.stock.data.upper(), user_id = user1.id).first()
			total_quantity = asset.quantity + form.quantity.data
			print(total_quantity)
			asset.quantity = total_quantity
			db.session.commit()
		else:
			asset = Assets(stock = form.stock.data.upper(), quantity = form.quantity.data , user_id = user1.id)
			db.session.add(asset)
			db.session.commit()
		Trans = Transaction_History(stock = form.stock.data.upper(), position = 1, price = form.price.data, 
			quantity = form.quantity.data, commission_type = account.commission_type, commission = round(commission_stock,2),
			total = round(stock_valuation + commission_stock,2),  user_id = user1.id)	
		account = Account.query.filter_by(user_id = user1.id).first()
		print(stock_valuation_commission)
		account.money -= stock_valuation_commission
		account.asset_value += stock_valuation
		account.total = account.money + account.asset_value
		db.session.add(Trans)
		db.session.commit()
		print(User.query.all())
		print(Account.query.all())
		print(Assets.query.all())
		print(Transaction_History.query.all())
		flash('You have successfully bought this stock', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		if fav:
			if fav.stock_code:
				r = requests.get(url.format(fav.stock_code.upper())).json()
				form.stock.data = fav.stock_code
				form.price.data = r['Global Quote']['05. price']
			if fav.stock_code1 and fav.stock_code is  None:
				r = requests.get(url.format(fav.stock_code1.upper())).json()
				form.stock.data = fav.stock_code1
				form.price.data = r['Global Quote']['05. price']

	return render_template('trading_buy.html', title = 'Buy', form = form, account = account,asset=asset,
		rounded_stock_value= rounded_stock_value, rounded_account=rounded_account)


@app.route("/trades/sell", methods = ['GET', 'POST'])
@login_required
def trades_sell():
	form = BuySellForm()
	#databases
	fav = Fav_Stock.query.filter_by(user_id = current_user.id).first()
	account = Account.query.filter_by(user_id = current_user.id).first()
	asset = Assets.query.filter_by(user_id = current_user.id)
	user1 = User.query.filter_by(username = current_user.username).first()
	#for the tables
	rounded_stock_value = {}
	url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey=demo=MD4DGMJPV06DEGG1'
	total_stock_value = 0
	for stocks in asset:
		r = requests.get(url.format(stocks.stock.upper())).json()
		r = r['Global Quote']['05. price']
		stocks.price = r
		stocks.total = float(stocks.price) * float(stocks.quantity)
		rounded_stock_value[stocks.stock.upper()] = round(stocks.total,2)
		db.session.commit()
		total_stock_value += float(stocks.total)
	rounded_account = [round(account.money,2), round(account.asset_value,2), round(account.total, 2)]
	print(fav)
	print(User.query.all())
	print(Account.query.all())
	print(Assets.query.all())
	print(Transaction_History.query.all())
	if form.validate_on_submit():
		current_asset = Assets.query.filter_by(stock = form.stock.data.upper(), user_id = user1.id).first()
		stock_valuation = form.price.data * form.quantity.data
		if account.commission_type ==	 True:
			commission_stock = stock_valuation * account.commission/100
		else:
			commission_stock = account.commission
		print(commission_stock)
		if current_asset is None:
			flash('You do not have the ability to short-sell', 'danger')
			return redirect(url_for('trades_sell'))
		elif form.quantity.data>current_asset.quantity:
			flash('You do not have the ability to short-sell', 'danger')
			return redirect(url_for('trades_sell'))
		else:
			asset = Assets.query.filter_by(stock = form.stock.data.upper(), user_id = user1.id).first()
			total_quantity = asset.quantity - form.quantity.data
			print(total_quantity)
			asset.quantity = total_quantity
			if total_quantity == 0:
				db.session.delete(asset)
			db.session.commit()
		Trans = Transaction_History(stock = form.stock.data.upper(), position = 0, price = form.price.data,
		 quantity = form.quantity.data, commission_type = account.commission_type, commission = round(commission_stock,2),
		 total = round(stock_valuation + commission_stock,2), user_id = user1.id)	
		account = Account.query.filter_by(user_id = user1.id).first()
		account.money += (stock_valuation - commission_stock)
		account.asset_value -= stock_valuation
		account.total = account.money + account.asset_value
		db.session.add(Trans)
		db.session.commit()
		print(User.query.all())
		print(Account.query.all())
		print(Assets.query.all())
		print(Transaction_History.query.all())
		flash('You have successfully sold this stock', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		if fav:
			if fav.stock_code:
				r = requests.get(url.format(fav.stock_code.upper())).json()
				form.stock.data = fav.stock_code
				form.price.data = r['Global Quote']['05. price']
			if fav.stock_code1 and fav.stock_code is None:
				r = requests.get(url.format(fav.stock_code1.upper())).json()
				form.stock.data = fav.stock_code1
				form.price.data = r['Global Quote']['05. price']
	return render_template('trading_sell.html', title = 'Sell', form = form, account = account, asset=asset,
		rounded_stock_value= rounded_stock_value, rounded_account=rounded_account)

@app.route("/research", methods=['GET', 'POST'])
@login_required
def research():
	form = StockForm()
	r_latest = {}
	r_latest_fav =[]
	url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey=demo=MD4DGMJPV06DEGG1'
	favourites = Fav_Stock.query.filter_by(user_id = current_user.id).all()
	print(favourites)
	for favs in favourites:
		if favs.stock_code != None:
			r = requests.get(url.format(favs.stock_code.upper())).json()
			r_latest = {
			'stock' : favs.stock_code.upper(),
			'open' : r['Global Quote']['02. open'],
			'high' : r['Global Quote']['03. high'],
			'low' : r['Global Quote']['04. low'],
			'close' :  r['Global Quote']['05. price'],
			'volume' : r['Global Quote']['06. volume'],
			}
			r_latest_fav.append(r_latest)
	if form.validate_on_submit():
		r = requests.get(url.format(form.stock.data.upper())).json()
		if form.add_favourite.data == False:
			r_latest = {
			'stock' : form.stock.data.upper(),
			'open' : r['Global Quote']['02. open'],
			'high' : r['Global Quote']['03. high'],
			'low' : r['Global Quote']['04. low'],
			'close' :  r['Global Quote']['05. price'],
			'volume' : r['Global Quote']['06. volume'],
			}
			if Fav_Stock.query.filter_by(user_id = current_user.id).first():
				current_fav = Fav_Stock.query.filter_by(user_id = current_user.id).first()
				current_fav.stock_code1 = form.stock.data.upper()
				db.session.commit()
			else:
				new_fav = Fav_Stock(stock_code1 = form.stock.data.upper(),  user_id = current_user.id)
				db.session.add(new_fav)
				db.session.commit()
		elif form.add_favourite.data == True:
			current_fav = Fav_Stock.query.filter_by(user_id = current_user.id).first()
			if current_fav:
				if current_fav.stock_code == form.stock.data.upper():
					flash('The stock is already in the Favourite List', 'danger')
					return redirect(url_for('research'))
				else:
					current_fav.stock_code = form.stock.data.upper()
					db.session.commit()
					return redirect(url_for('research'))
			else:
				new_fav = Fav_Stock(stock_code = form.stock.data.upper(),  user_id = current_user.id)
				db.session.add(new_fav)
				db.session.commit()
				return redirect(url_for('research'))


	return render_template('research.html', title = 'Research', form = form, r_latest = r_latest, r_latest_fav=r_latest_fav)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_pathway = os.path.join(app.root_path, 'static/Images', picture_fn)
	
	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_pathway)

	return picture_fn



@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
	form = UpdateForm()	
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
			db.session.commit()
			flash('Your display picture has been updated', 'success')
			return redirect(url_for('profile'))
		elif form.username.data!=current_user.username:
			current_user.username = form.username.data
			db.session.commit()
			flash(f'Your username has been updated to : {form.username.data}', 'success')
			return redirect(url_for('profile'))
		elif form.email.data!=current_user.email:
			current_user.email = form.email.data
			db.session.commit()
			flash(f'Your email has been updated to : {form.email.data}', 'success')
			return redirect(url_for('profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename = 'Images/' + current_user.image_file)
	return render_template('profile.html', title = 'Profile', form = form , image_file=image_file)


@app.route("/account")
@login_required
def account():
	rounded_stock_value = {}
	asset = Assets.query.filter_by(user_id = current_user.id).all()
	account = Account.query.filter_by(user_id = current_user.id).first()	
	url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey=demo=MD4DGMJPV06DEGG1'
	total_stock_value = 0
	for stocks in asset:
		r = requests.get(url.format(stocks.stock.upper())).json()
		r = r['Global Quote']['05. price']
		stocks.price = r
		stocks.total = float(stocks.price) * float(stocks.quantity)
		rounded_stock_value[stocks.stock.upper()] = round(stocks.total,2)
		db.session.commit()
		total_stock_value += float(stocks.total)
	account.asset_value = total_stock_value
	account.total = account.money + account.asset_value
	db.session.commit()
	rounded_account = [round(account.money,2), round(account.asset_value,2), round(account.total, 2)]
	rounded_th = {}
	transaction_history = Transaction_History.query.filter_by(user_id = current_user.id).all()
	return render_template('account.html', title = 'Account', account = account, asset = asset,
		rounded_stock_value= rounded_stock_value, rounded_account=rounded_account, transaction_history=transaction_history)

# 1 is percentage and 0 fixed

@app.route("/account/restart", methods=['GET', 'POST'])    
@login_required
def account_restart():
	form = AccountForm()
	user1 = User.query.filter_by(username = current_user.username).first()
	account1 = Account.query.filter_by(user_id = user1.id).first()
	assets1 = Assets.query.filter_by(user_id = user1.id).all()
	th1 = Transaction_History.query.filter_by(user_id = user1.id).all()	
	if form.validate_on_submit():
		account1.money= form.money.data
		account1.asset_value = 0
		account1.total = form.money.data
		for each in assets1:
			db.session.delete(each)
		for each in th1:
			db.session.delete(each)
		db.session.commit()
		print(User.query.all())
		print(Account.query.all())
		print(Assets.query.all())
		print(Transaction_History.query.all())	
		flash(f'Your account has be reset and you can now trade with ${form.money.data}', 'success')
		return redirect(url_for('account'))
	print(user1, account1,assets1,th1,'check2')
	return render_template('account_restart.html', title = 'Account Restart', form = form)

@app.route("/account/commission", methods=['GET', 'POST'])    
@login_required
def commission_restart():
	c_form = CommissionForm()
	user1 = User.query.filter_by(username = current_user.username).first()
	account1 = Account.query.filter_by(user_id = user1.id).first()
	assets1 = Assets.query.filter_by(user_id = user1.id).all()
	th1 = Transaction_History.query.filter_by(user_id = user1.id).all()	
	if c_form.validate_on_submit():
		if c_form.commission_type_f.data == True and c_form.commission_type_p.data == True:
			flash('You can choose either a percentage or a fixed commission', 'danger')
			return redirect(url_for('commission_restart'))
		elif c_form.commission_type_f.data == True:
			account1.commission_type = False
			account1.commission = c_form.fixed.data
			print(account1)
		elif c_form.commission_type_p.data == True:
			account1.commission_type = True
			account1.commission = c_form.percentage.data
			print(account1)
		db.session.commit()
		flash(f'Your commission status has been has be reset', 'success')
		return redirect(url_for('account'))
	return render_template('commission_restart.html', title = 'Commission Restart', c_form = c_form)

@app.route("/password_forgotten")
def password_f():
	return render_template('password1.html', title = 'password')

@app.route("/about")
def about():
	return render_template('about.html',title='about')

	
@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('profile'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(user)
		db.session.commit()
		account1 = Account(money = 100000, asset_value=0, total = 100000, user_id = user.id)
		db.session.add(account1)
		db.session.commit()
		flash(f'Your account has been created, you can login as	 {form.username.data}', 'success')
		return redirect(url_for('home'))

	return render_template('register.html', title = 'register', form = form)
