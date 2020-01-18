
from app import db
from flask import render_template, flash, redirect, url_for, request, current_app
from app.todo.forms import TaskForm, SubtaskForm, SubtaskCompletionForm
from app.models import User, Task, Subtask
from app.todo import bp
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
import datetime
import dateutil.relativedelta as rel

@bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
	form = TaskForm()
	if form.validate_on_submit():
		task = Task(name=form.task.data, doer=current_user)
		db.session.add(task)
		db.session.commit()
		flash('Your task is added!')
		return redirect(url_for('todo.tasks'))

	#getting days left
	weekdays={0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
	today=datetime.date.today()
	weekday=datetime.date.weekday(today)
	days_left = 7-weekday
	weekday=weekdays[weekday]
	#Getting all tasks for the current_user
	weekly_tasks = Task.query.filter(Task.user_id == current_user.id, Task.n_subtasks>0)
	daily_tasks = Task.query.filter(Task.user_id == current_user.id, Task.n_subtasks == 0)
	return  render_template('todo/tasks_home.html', title='Home', today=today, days_left=days_left,weekday=weekday,form=form,daily_tasks = daily_tasks, weekly_tasks = weekly_tasks)

@bp.route('/task/<id>', methods=['GET', 'POST'])
@login_required
def task(id):
	#Adding a new subtask
	form = SubtaskForm()
	task = Task.query.filter_by(id=id).first()
	if form.validate_on_submit():
		subtask = Subtask(name=form.subtask.data, task=task)
		task.n_subtasks+=1
		db.session.add(subtask)
		db.session.commit()
		flash('Your subtask is added!')
		return redirect(url_for('todo.task',id=id))

	#Getting completed subtasks via checkboxes
	if request.method=='POST':
		checked_ids=request.form.getlist('status_checkbox')
		all_subtasks=Subtask.query.filter_by(task_id=id)
		for subtask in all_subtasks:
			if str(subtask.id) in checked_ids:
				subtask.check()
			else:
				subtask.uncheck()
		return redirect(url_for('todo.task', id=id))
	#checked_subtasks, unchecked_subtasks
	uc_subtasks = Subtask.query.filter_by(task_id=id, status=0)
	c_subtasks = Subtask.query.filter_by(task_id=id, status=1)
	return render_template('todo/task.html', form=form, task = task, c_subtasks = c_subtasks, uc_subtasks=uc_subtasks)


@bp.route('/delete_task/<id>')
@login_required
def delete_task(id):
	Subtask.query.filter_by(task_id = id).delete()
	Task.query.filter_by(id = id).delete()
	db.session.commit()
	flash('Task deleted successfully')
	return redirect(url_for('todo.tasks'))
