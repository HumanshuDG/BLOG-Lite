from flask import Flask, Blueprint, render_template, flash, request, redirect, Response, url_for
import mimetypes
from application.models import User, Blog, Like, Comment
from application.database import db
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import matplotlib.pyplot as plt
from flask import current_app as app


cont = Blueprint('controllers', __name__)

user_state = current_user

login_manager = LoginManager()

# @login_manager.unauthorized_handler
# def unauthorized():
#   flash("You're not authorised.Please login for further access to site.")
#   return redirect(url_for('controller.login'))


##############################################################
##############################################################
#######                AUTHENTICATION                 ########
##############################################################
##############################################################
@cont.route("/logout", methods = ['GET', 'POST'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('controllers.login'))


@cont.route('/', methods = ['GET', 'POST'])
def landing():
	return redirect(url_for('controllers.signup'))


@cont.route('/signup', methods = ['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form.get('username')
		pass_one = request.form.get('password1')
		pass_two = request.form.get('password2')
		user = User.query.filter_by(username = username).first()
		image = open('application/static/assets/img/user.png', 'rb').read()
		if user:
			flash('Username already exists!', category='error')
		elif len(username) < 2:
			flash('Please enter longer username!', category='error')
		elif pass_one != pass_two:
			flash('Passwords do not match!', category='error')
		elif len(pass_one) < 4:
			flash('Too short password!', category='error')
		else:
			new_user = User(username = username, password = generate_password_hash(pass_one, method = 'sha256'), bio = '', display_picture = image, dp_mimetype = 'image/png')
			db.session.add(new_user)
			db.session.commit()

			login_user(new_user, remember = True)
			flash('Sign Up Successful!', category = 'success')
			return redirect(url_for('controllers.home'))
	return render_template('/auth/signup.html')


@cont.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		user = User.query.filter_by(username = username).first()
		if user:
			if check_password_hash(user.password, password):
				login_user(user, remember = True)
				return redirect(url_for('controllers.home'))
			else:
				flash('Incorrect Password!', category='error')
	return render_template('auth/login.html')


@cont.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
	followings = [user.user_id for user in current_user.followed]
	followings.append(current_user.user_id)
	blogs = Blog.query.filter(Blog.auth_id.in_(followings))
	if user_state:
		return render_template('home.html',
							   logged_in = user_state,
							   blogs = blogs
							  )
	else:
		return render_template('auth/login.html')


##############################################################
##############################################################
#######          EXPLORE PAGE WITH ALL POSTS          ########
##############################################################
##############################################################
@cont.route('/explore')
@login_required
def explore():
	blogs = Blog.query.all()
	return render_template('explore.html', logged_in = user_state, blogs = blogs)


##############################################################
##############################################################
#######                 CRUD ON BLOG                  ########
##############################################################
##############################################################
@cont.route('/create-blog', methods = ['GET', 'POST'])
@login_required
def create_blog():
	return render_template('create-blog.html', logged_in = user_state)


@cont.route('/add-blog', methods = ['GET', 'POST'])
@login_required
def add_blog():
	image = request.files['image']
	title = request.form.get('title')
	caption = request.form.get('caption')
	mimetype = image.mimetype
	user_id = current_user.user_id
	blog = Blog(
					auth_id = user_id,
					blog_title = title,
					blog_photo = image.read(),
					blog_caption = caption,
					blog_photo_mimetype = mimetype
			   )
	db.session.add(blog)
	db.session.commit()
	flash('Blog posted successfully!', category = 'success')
	return redirect(request.referrer)

@cont.route('/edit-blog/<blog_id>', methods = ['GET', 'POST'])
@login_required
def edit_blog(blog_id):
	blog = Blog.query.filter_by(blog_id = blog_id).first()
	return render_template('edit-blog.html', blog = blog)


@cont.route('/update-blog/<blog_id>', methods = ['GET', 'POST'])
@login_required
def update_blog(blog_id):
	blog = Blog.query.filter_by(blog_id = blog_id).first()
	if blog is None:
		flash('Post not found!', category='danger')
	image = request.files['image']
	title = request.form.get('title')
	caption = request.form.get('caption')
	mimetype = image.mimetype
	user_id = current_user.user_id
	if title:
		blog.blog_title = title
	if caption:
		blog.blog_caption = caption
	if image:
		blog.blog_photo = image.read()
		blog.blog_photo_mimetype = mimetype
	db.session.commit()
	flash('Blog updated successfully!', category = 'success')
	return redirect(request.referrer)


@cont.route('/delete-blog/<blog_id>', methods = ['GET', 'POST'])
@login_required
def delete_blog(blog_id):
	blog = Blog.query.filter_by(blog_id = blog_id).first()
	db.session.delete(blog)
	db.session.commit()
	flash('Blog deleted successfully!', category = 'success')
	return redirect(request.referrer)


@cont.route('/blog/<int:blog_id>', methods = ['GET', 'POST'])
@login_required
def blog(blog_id):
	blog = Blog.query.get_or_404(blog_id)
	return render_template('post.html', logged_in = user_state, blog = blog)


##############################################################
##############################################################
#######                  PHOTO LINKS                  ########
##############################################################
##############################################################
@cont.route('/user-photo/<int:user_id>')
@login_required
def user_photo(user_id):
    user = User.query.filter_by(user_id = user_id).first()
    return Response(user.display_picture)#, mimetype = user.dp_mimetype)


@cont.route('/blog-photo/<int:blog_id>')
@login_required
def blog_photo(blog_id):
    blog = Blog.query.filter_by(blog_id = blog_id).first()
    return Response(blog.blog_photo, mimetype = blog.blog_photo_mimetype)


##############################################################
##############################################################
#######                   COMMENTS                    ########
##############################################################
##############################################################
@cont.route('/add-comment/<int:blog_id>', methods = ['POST'])
@login_required
def add_comment(blog_id):
	comment_ = request.form.get('comment')
	if comment_ is None:
		flash('Comment cannot be empty string!', category = 'danger')
	comment = Comment(
		auth_id = current_user.user_id,
		blog_id = blog_id,
		comment = comment_
	)
	db.session.add(comment)
	db.session.commit()
	flash('Comment Added!', category = 'success')
	return redirect(request.referrer)

@cont.route('/delete-comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
	comment = Comment.query.filter_by(comment_id = comment_id).first()
	if comment is None:
		flash('Comment not found!', category = 'danger')
		return redirect(request.referrer)
	# try:
	db.session.delete(comment)
	db.session.commit()
	flash('Comment Deleted!', category = 'success')
	return redirect(request.referrer)


##############################################################
##############################################################
#######                     LIKES                     ########
##############################################################
##############################################################
@cont.route('/add-like/<int:blog_id>', methods = ['GET', 'POST'])
@login_required
def add_like(blog_id):
	like = Like.query.filter_by(blog_id = blog_id, user_id = current_user.user_id).first()
	if like:
		db.session.delete(like)
		db.session.commit()
	else:
		like = Like(user_id = current_user.user_id, blog_id = blog_id)
		db.session.add(like)
		db.session.commit()
		flash('Post Liked!', category = 'success')
	return redirect(request.referrer)

##############################################################
##############################################################
#######            USER PROFILE MANAGEMENT            ########
##############################################################
##############################################################
@cont.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
	user = current_user
	return render_template('profile.html', logged_in = user_state, user = current_user)


@cont.route('/edit-profile/<user_id>', methods = ['GET', 'POST'])
@login_required
def edit_profile(user_id):
	user = User.query.filter_by(user_id = user_id).first()
	return render_template('edit-profile.html', logged_in = user_state, user = user)

@cont.route('/update-profile/<user_id>', methods = ['GET', 'POST'])
@login_required
def update_profile(user_id):
	user = User.query.filter_by(user_id = user_id).first()
	if user is None:
		flash('User not found!', category='danger')
	image = request.files['image']
	username = request.form.get('username')
	bio = request.form.get('bio')
	mimetype = image.mimetype
	if username:
		user.username = username
	if bio:
		user.bio = bio
	if image:
		user.display_picture = image.read()
		user.dp_mimetype = mimetype
	db.session.commit()
	flash('Profile updated successfully!', category = 'success')
	return redirect(request.referrer)


@cont.route('/user/<username>', methods = ['GET', 'POST'])
@login_required
def user(username):
	user = User.query.filter_by(username = username).first()
	user_id = user.user_id
	user = User.query.filter_by(user_id = user_id).first()
	# follower = User.query.join(followers).join(User).filter((followers.c.follower_id == User.user_id), (followers.c.followed_id)).all()
	return render_template('user.html',
						   logged_in = user_state,
						   user = user#,
						   # followers = follower
						  )

##############################################################
##############################################################
#######                FOLLOW/UNFOLLOW                ########
##############################################################
##############################################################
@cont.route('/follow-user/<username>', methods = ['GET', 'POST'])
@login_required
def follow_user(username):
	user = User.query.filter_by(username = username).first()
	current_user.followed.append(user)
	db.session.commit()
	flash('You just followed ' + username + '!')
	return redirect(url_for('controllers.user', username = username))

@cont.route('/unfollow-user/<username>', methods = ['GET', 'POST'])
@login_required
def unfollow_user(username):
	user = User.query.filter_by(username = username).first()
	current_user.followed.remove(user)
	db.session.commit()
	flash('You just followed ' + username + '!')
	return redirect(url_for('controllers.user', username = username))

@cont.route('/user/<username>/followings')
@login_required
def followings():
	
	return render_template('list.html', logged_in = user_state)


@cont.route('/user/<username>/followers')
@login_required
def followers(username):
	followers_ = User.query.join(followers).join(User).filter_by(User.c.followed_id == username).all()
	return render_template('list.html', logged_in = user_state, users = followers_)

# query_user_role = User.query.join(roles_users).join(Role).filter((roles_users.c.user_id == User.id) & (roles_users.c.role_id == Role.id)).all()

@cont.route('/search', methods = ['GET', 'POST'])
@login_required
def search():
	return render_template('search.html', logged_in = user_state)


@cont.route('/search-user', methods = ['GET', 'POST'])
@login_required
def search_user():
	query = request.form.get('query')
	if query is None:
		flash('Please enter something to search..')
	users = User.query.filter(User.username.contains(query), User.username.contains(query)).all()
	return render_template('list.html', logged_in = user_state, users = users)

@cont.route('/test')
def test():
	return render_template('test.html', logged_in = user_state)