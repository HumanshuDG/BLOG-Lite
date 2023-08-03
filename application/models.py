from application.database import db
from flask_login import UserMixin
from sqlalchemy.sql import func


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.user_id'))
)


class User(db.Model, UserMixin):
	__tablename__ = 'user'
	user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	username = db.Column(db.Text, unique = True, nullable = False)
	password = db.Column(db.Text, unique = False)
	bio = db.Column(db.Text)
	display_picture = db.Column(db.Text)
	dp_mimetype = db.Column(db.Text)
	
	blogs = db.relationship('Blog', backref = 'user', lazy = True)
	likes = db.relationship('Like', cascade = 'all, delete', backref = 'user')
	comments = db.relationship('Comment', cascade = 'all, delete', backref = 'user')
	followed = db.relationship(
								'User',
								secondary = 'followers',
								cascade = 'all, delete',
								primaryjoin = (followers.c.follower_id == user_id),
								secondaryjoin = (followers.c.followed_id == user_id),
								backref = db.backref('followers', lazy = 'joined')
							)
	def get_id(self):
		return self.user_id

	# def follows(self, User):
	# 	return self.followers.filter_by(followers.followed_id == User.user_id).count() > 0

	def __repr__(self):
		return  {	
					'username': '{self.username}',
					'password': '{self.password}',
					'bio': '{self.bio}',
					'image': '{self.display_picture}',
					'image_mimetype': '{self.dp_mimetype}'
				}
	


class Blog(db.Model):
	__tablename__ = 'blog'
	blog_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	auth_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	blog_title = db.Column(db.Text, nullable = False)
	blog_photo = db.Column(db.Text, nullable = False)
	blog_photo_mimetype = db.Column(db.Text, nullable = False)
	blog_caption = db.Column(db.Text, nullable = True)
	timestamp = db.Column(db.DateTime(timezone = True), default = func.now())
	blog_like = db.relationship('Like', backref = 'blog', cascade = 'all, delete')
	blog_comment = db.relationship('Comment', backref = 'blog', cascade = 'all, delete')

	def __repr__(self):
		return  f"""{
						blog_id: '{self.blog_id}',
						author_id: '{self.user_id}',
						title: '{self.blog_title}',
						image: '{self.blog_photo}',
						image_mimetype: '{self.blog_photo_mimetype}'
					}"""



class Like(db.Model):
	__tablename__ = 'like'
	like_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete= 'CASCADE'), nullable = False)
	blog_id = db.Column(db.Integer, db.ForeignKey('blog.blog_id', ondelete= 'CASCADE'), nullable = False)
	# like_author = db.relationship('User', foreign_keys = [user_id], backref = 'user')

	def __repr__(self):
		return  f"""{
						like_id: '{self.like_id}',
						user_id: '{self.user_id}',
						blog_id: '{self.blog_id}'
					}"""



class Comment(db.Model):
	__tablename__ = 'comment'
	comment_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	auth_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete= 'CASCADE'), nullable = False)
	blog_id = db.Column(db.Integer, db.ForeignKey('blog.blog_id', ondelete= 'CASCADE'), nullable = False)
	comment = db.Column(db.Text)
	timestamp = db.Column(db.DateTime(timezone = True), default = func.now())
	# comment_author = db.relationship('User', foreign_keys = [auth_id], cascade = 'all, delete', backref = 'user')

	def __repr__(self):
		return  f"""{
						comment_id: '{self.comment_id}',
						user_id: '{self.user_id}',
						blog_id: '{self.blog_id}',
						comment: '{self.comment}',
						timestamp: '{self.timestamp}'
					}"""