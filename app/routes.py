
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, TaskForm, SubtaskForm, SubtaskCompletionForm
from app.models import User, Task, Subtask
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
import datetime 
import dateutil.relativedelta as rel


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = TaskForm()
	if form.validate_on_submit():
		task = Task(name=form.task.data, doer=current_user)
		db.session.add(task)
		db.session.commit()
		flash('Your task is added!')
		return redirect(url_for('index'))
	
	#getting days left
	weekdays={0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
	today=datetime.date.today()
	weekday=datetime.date.weekday(today)
	days_left = 7-weekday
	weekday=weekdays[weekday]
	#Getting all tasks for the current_user
	tasks = Task.query.filter_by(user_id = current_user.id)
	return  render_template('index.html', title='Home', today=today, days_left=days_left,weekday=weekday,form=form,tasks = tasks)

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
	tasks = Task.query.filter_by(user_id=user.id)
	return render_template('user.html', user=user, tasks=tasks)

@app.route('/task/<id>', methods=['GET', 'POST'])
@login_required
def task(id):
	#Adding a new subtask
	form = SubtaskForm()
	task = Task.query.filter_by(id=id).first()
	if form.validate_on_submit():
		subtask = Subtask(name=form.subtask.data, task=task)
		db.session.add(subtask)
		db.session.commit()
		flash('Your subtask is added!')
		return redirect(url_for('task',id=id))
		
	#Getting completed subtasks via checkboxes	
	if request.method=='POST':
		checked_ids=request.form.getlist('status_checkbox')
		all_subtasks=Subtask.query.filter_by(task_id=id)
		for subtask in all_subtasks:
			if str(subtask.id) in checked_ids:
				subtask.check()
			else:
				subtask.uncheck()
			
		return redirect(url_for('task', id=id))
	#checked_subtasks, unchecked_subtasks
	uc_subtasks = Subtask.query.filter_by(task_id=id, status=0)
	c_subtasks = Subtask.query.filter_by(task_id=id, status=1)
	return render_template('task.html', form=form, task = task, c_subtasks = c_subtasks, uc_subtasks=uc_subtasks)
	
	
	
	
	
	
	
	
	
	
	
	
	
