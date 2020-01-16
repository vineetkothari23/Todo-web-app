from flask_wtf import FlaskForm, widgets
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from app.models import User

class TaskForm(FlaskForm):
	task = TextAreaField('Your task name', validators=[DataRequired(), Length(min=1, max=50)])
	submit = SubmitField('Submit')

class SubtaskForm(FlaskForm):
	subtask = TextAreaField('', validators=[DataRequired(), Length(min=1, max=50)],description='Add your subtasks')
	submit = SubmitField('Add')

class SubtaskCompletionForm(FlaskForm):
	status = BooleanField('')
	#submit = SubmitField('Sign In')
