from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
from flask import request

class CreateChallengeForm(FlaskForm):
	name = StringField('Name', validators = [DataRequired()])
	description = TextAreaField('About the challenge', validators = [Length(min = 0, max = 600)])
	total_days = StringField('Total days', validators=[DataRequired()])
	interval = StringField('Interval')
	type = StringField('Type')
	submit = SubmitField('Add challenge')

class EditChallengeForm(FlaskForm):
	description = TextAreaField('About the challenge', validators = [Length(min = 0, max = 600)])
	total_days = StringField('Total days', validators=[DataRequired()])
	interval = StringField('Interval')
	submit = SubmitField('Edit challenge')

	def __init__(self, *args, **kwargs):
		super(EditChallengeForm, self).__init__(*args, **kwargs)
