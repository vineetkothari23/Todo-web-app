from flask_wtf import FlaskForm, widgets
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
	'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
 # Checking for unique username
	def validate_username(self, username):
		user=User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')
	#Checking for unique email
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')

class TaskForm(FlaskForm):
	task = TextAreaField('Your task name', validators=[DataRequired(), Length(min=1, max=50)])
	submit = SubmitField('Submit')
	
class SubtaskForm(FlaskForm):
	subtask = TextAreaField('Your subtask name', validators=[DataRequired(), Length(min=1, max=50)])
	submit = SubmitField('Submit')

class SubtaskCompletionForm(FlaskForm):
	status = BooleanField('')
	#submit = SubmitField('Sign In')
