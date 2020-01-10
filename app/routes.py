
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
#@login_required
def index():
	tasks = [{'task_name':"task_1"},{'task_name':"task_2"}]
	return  render_template('index.html', title='Home',tasks = tasks)

@app.route('/login',methods=['GET','POST'])
def login():
	#if already logging in, redirect to home page
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		#Getting the user with the username from db
		user=User.query.filter_by(username=form.username.data).first()
	# Check if the login is correct
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login')) # here login is the reference of the function name login()
		# Login  the user as the 'current_user'
		login_user(user, remember=form.remember_me.data)
		#Redirection after logging in
		# Redirecting to the same site, incase of malicious URL. Ref article
		next_page=request.args.get('next')
		if not next_page or url_parse(next_page).netloc!='':
			next_page=url_for('index')
			return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user=User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
	{'author': user, 'body': 'Test post #1'},
	{'author': user, 'body': 'Test post #2'}
	]
	return render_template('user.html', user=user, posts=posts)
