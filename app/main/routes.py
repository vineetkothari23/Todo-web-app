from flask import current_app, g
from app import  db
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post, Challenge, Task
from app.auth.email import send_password_reset_email
from flask import render_template,flash,redirect,url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from app.main import bp
import re
import os

@bp.before_app_request
def before_request():
	if current_user.is_authenticated:
		# Adding the recurring task

		#For all challenges

		#CASE 1: if the current time - last seen > challenge interval
	    #		 1.2 : and the task status = "Active on track",
		#				 change status to "Active pending"
		#		1.3:  and the task status = "Active pending"
		# 			, Change task status = "Active begin", Set streak = 0
		#CASE 2: if the task status = 'Active begin',
		#			,set streak to 0 and change task status = 'Acive pending'
		#CASE 3: if the task status = 'Active complete',
		#			, do nothing
		time_dict={0:timedelta(seconds=30).total_seconds(),
					1: timedelta(days=7).total_seconds(),
					2:	timedelta(days=30).total_seconds()}
		current_time =  datetime.utcnow()
		last_seen = current_user.last_seen if current_user.last_seen!=None else current_time
		try:
			time_diff = (current_time-last_seen).total_seconds()
		except:
			print('Problem with time subtraction',current_time," and ", last_seen)

		for challenge in current_user.challenges_followed:
			task = Task.query.filter_by(challenge=challenge).first()
			if task!=None or task.status!='Complete':
				if time_diff > time_dict[challenge.interval]:
					if task.status == 'Active on track' and task.streak < challenge.total_days:
						task.set_status('Active pending')
					elif task.status == 'Active pending':
						#add reset_streak()
						task.steak=0
						db.session.commit()

				#else: do nothing

			#else: do nothing

		#Setting the last seen of the User
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
		g.search_form = SearchForm()
		Post.reindex()
		Challenge.reindex()
		User.reindex()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/',methods=['GET', 'POST'])
@bp.route('/index',methods=['GET', 'POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		body=form.post.data
		hashtags=re.findall(r"#(\w+)", body)
		if len(hashtags)>0:
			challenge_name=hashtags[0]
			challenge = Challenge.query.filter_by(name = challenge_name).first()
			if challenge is not None and challenge.followed_by(current_user):
				post = Post(body=form.post.data, author=current_user, challenge=challenge)
				db.session.add(post)
				db.session.commit()
				flash('Your post is live now!')
				return redirect(url_for('main.index'))
			else:
				flash('You are not following the challenge or the challenge does not exist!')
				return redirect(url_for('main.index'))
		else:
			flash('The first hashtag should be a challenge name')
			return redirect(url_for('main.index'))

	page = request.args.get('page', 1, type=int)
	#Paginate takes three arguments
	# The current page no.
	# No of posts per page
	# error flage: if tru, requests 404 page.
	posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title='Home page',form=form,posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
	page = request.args.get('page',1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	#Checcking if are there more posts available to paginate to next page
	next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title = 'Explore', posts = posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
	user=User.query.filter_by(username=username).first_or_404()

	#Getting user posts
	page= request.args.get('page', 1, type=int)
	posts=Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_next else None

	#Getting followers
	followers = user.followers
	#TODO: Need to add pagination.
	return render_template('user.html',user=user,posts=posts.items, next_url=next_url, prev_url=prev_url,
							followers=followers)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
	user = User.query.filter_by(username = username).first_or_404()
	return render_template('user_popup.html', user=user)


from flask import send_from_directory

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@bp.route('/follow/<username>')
@login_required
def follow(username):
	user=User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash('You cannot follow yourself')
		return redirect(url_for('main.user', username = username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('main.user', username = username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username = username)
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash('You cannot unfollow yourself')
		return redirect(url_for('main.user', username = username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You have stopped following {}!'.format(username))
	return redirect(url_for('main.user', username = username))

# @bp.route('/edit_profile', methods = ['GET', 'POST'])
# @login_required
# def edit_profile():
# 	if request.method == 'POST':
# 		if 'file' not in request.files:
# 			flash('No file part')
# 			return redirect(request.url)
# 	file = request.files['file']
# 	if file.filename == '':
# 		flash('No selected file')
# 		return redirect(request.url)
# 	if file and allowed_file(file.filename):
# 		filename = secure_filename(file.filename)
# 		file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
# 		#current_user.set_profile_pic(filename)
# 		#db.session.commit()
# 		return redirect(url_for('main.uploaded_file',filename=filename))
# 	return render_template('add_profile_pic.html')

@bp.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		current_user.first_name = form.first_name.data
		current_user.last_name = form.last_name.data
		db.session.commit()
		flash(_('Your changes have been saved.'))
		return redirect(url_for('main.edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
		form.first_name.data = current_user.first_name
		form.last_name.data = current_user.last_name
	return render_template('edit_profile.html', title='Edit Profile',form=form)

@bp.route('/search')
@login_required
def search():

	# if not g.search_form.validate():
	# 	return redirect(url_for('main.explore'))
	page = request.args.get('page', 1, type=int)
	posts, total_posts = Post.search(g.search_form.q.data, page,
			       current_app.config['POSTS_PER_PAGE'])
	posts = posts if total_posts>0 else None
	next_posts_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
	if total_posts > page * current_app.config['POSTS_PER_PAGE'] else None
	prev_posts_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
	if page > 1 else None

	# users, total_users = User.search(g.search_form.q.data, page,current_app.config['POSTS_PER_PAGE'])
	# users = users if total_users>0 else None
	# next_users_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
	# if total_users > page * current_app.config['POSTS_PER_PAGE'] else None
	# prev_users_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
	# if page > 1 else None
	users=None
	prev_users_url=None
	next_users_url=None

	# page = request.args.get('page', 1, type=int)
	challenges, total_pages = Challenge.search(g.search_form.q.data, page,
			       current_app.config['POSTS_PER_PAGE'])
	challenges = challenges if total_pages>0 else None
	next_pages_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
	if total_pages > page * current_app.config['POSTS_PER_PAGE'] else None
	prev_pages_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
	if page > 1 else None

	return render_template('search.html', title='Search',
				   posts=posts, users= users, challenges=challenges,
		           next_posts_url=next_posts_url, prev_posts_url=prev_posts_url,
				   next_users_url=next_users_url, prev_users_url=prev_users_url,
				   next_pages_url=next_pages_url, prev_pages_url=prev_pages_url)

# @bp.context_processor
# def suggested_pages():
# 	challenges = Challenge.query.filter_by(id=2).first()
# 	return dict(challenges=challenges )
