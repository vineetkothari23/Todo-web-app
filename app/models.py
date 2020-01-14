from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	tasks = db.relationship('Task', backref='doer', lazy = 'dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)  	

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	n_subtasks = db.Column(db.Integer, index=True, default=0)
	nc_subtasks = db.Column(db.Integer, index=True, default=0)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	subtasks = db.relationship('Subtask', backref='task', lazy='dynamic')

	def __repr__(self):
		return '<Task {}>'.format(self.name)
	
	def completion_percent(self):
		nc_subtasks=self.recount_nc_subtasks()
		n_subtasks=self.recount_n_subtasks()
		percent=str(int(nc_subtasks*100/n_subtasks)) \
			if self.n_subtasks>0 else '0'		
		return percent
	
	def recount_n_subtasks(self):
		temp = Subtask.query.filter_by(task_id=self.id).count()
		self.n_subtasks=temp
		return temp

	def recount_nc_subtasks(self):
		temp = Subtask.query.filter_by(task_id=self.id,status=1).count()
		self.nc_subtasks = temp
		return temp


class Subtask(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	#1 is task complete, 0 is task incomplete 
	status = db.Column(db.Integer, index=True, default=0)
	task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

	def __repr__(self):
		return '<Subtask {} {}>'.format(self.name, self.status)

	def check(self):
		self.status=1
		db.session.commit()
	
	def uncheck(self):
		self.status=0
		db.session.commit()
	
   
	
	
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
