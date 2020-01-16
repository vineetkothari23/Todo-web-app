from flask import current_app,g
from app import  db
from app.pages import bp
from app.pages.forms import CreateChallengeForm, EditChallengeForm
from app.main.forms import  SearchForm
from app.models import User, Challenge, Post
from flask import render_template,flash,redirect,url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

# @bp.before_app_request
# def before_request():
# 	if current_user.is_authenticated:
# 		g.search_form = SearchForm()

@bp.route('/pages')
def pages():
	challenges=Challenge.query.all()
	return render_template('pages/pages_index.html',title='Challenges', challenges=challenges)

@bp.route('/add_page', methods = ['GET', 'POST'])
@login_required
def add_page():
	form = CreateChallengeForm()
	if form.validate_on_submit():
		challenge_name = form.name.data
		challenge = Challenge.query.filter_by(name=challenge_name).first()
		if challenge is None:
			challenge = Challenge(name = challenge_name,
								description = form.description.data,
								total_days=form.total_days.data,
								interval=form.interval.data,
								type=form.type.data,
								creator_id=current_user.id)
			db.session.add(challenge)
			db.session.commit()
			flash('New challenge {} created.'.format(challenge_name))
			return redirect(url_for('pages.challenge', pagename = challenge_name))
		else:
			flash('Challenge {} already exists.'.format(challenge_name))
			return redirect(url_for('pages.add_page'))

	return render_template('pages/add_page.html', title = 'New Challenge', form = form)

@bp.route('/delete_page/<pagename>')
@login_required
def delete_page(pagename):
	Challenge.query.filter_by(name = pagename).delete()
	db.session.commit()
	return redirect(url_for('pages.pages'))

@bp.route('/edit_page/<pagename>', methods = ['GET', 'POST'])
@login_required
def edit_page(pagename):
	challenge = Challenge.query.filter_by(name=pagename).first_or_404()
	form = EditChallengeForm()
	if form.validate_on_submit():
		description = form.description.data
		total_days=form.total_days.data
		interval=form.interval.data
		db.session.commit()
		flash(' Your changes have been saved. ')
		return redirect(url_for('pages.challenge', pagename=pagename))
	elif request.method == 'GET':
		form.description.data = challenge.description
		form.interval.data = challenge.interval
		form.total_days.data = challenge.total_days
	return render_template('pages/edit_profile.html', title = 'Edit challenge', form = form)

@bp.route('/challenge/<pagename>')
def challenge(pagename):
	challenge = Challenge.query.filter_by(name=pagename).first_or_404()
	page = request.args.get('page',1, type=int)
	posts = Post.query.filter_by(challenge_id=challenge.id).order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	#Checcking if are there more posts available to paginate to next page
	next_url = url_for('pages.challenge', pagename=pagename, page=posts.next_num) if posts.has_next else None
	prev_url = url_for('pages.challenge', pagename=pagename, page=posts.prev_num) if posts.has_prev else None
	#need to pass next_url and preev
	creator=User.query.filter_by(id=challenge.creator_id).first()
	return render_template('pages/challenge.html',challenge=challenge, posts=posts.items, prev_url=prev_url, next_url=next_url, creator = creator)

@bp.route('/follow_page/<pagename>')
@login_required
def follow_page(pagename):
	challenge = Challenge.query.filter_by(name=pagename).first()
	if challenge is None:
		flask('Challenge {} does not exist.'.format(pagename))
		return redirect(url_for('pages.pages'))
	else:
		challenge.follow_request(current_user)
		db.session.commit()
		flash('You are now following {}.'.format(pagename))
		return redirect(url_for('pages.pages'))

@bp.route('/unfollow_page/<pagename>')
@login_required
def unfollow_page(pagename):
	challenge = Challenge.query.filter_by(name=pagename).first()
	if challenge is None:
		flask('Challenge {} does not exist.'.format(pagename))
		return redirect(url_for('pages.pages'))
	else:
		challenge.unfollow_request(current_user)
		db.session.commit()
		flash('You stopped following {}.'.format(pagename))
		return redirect(url_for('pages.pages'))
