# https://youtu.be/TLrFUN5ZVyU

from flask_restful import Resource, Api, fields, marshal_with, reqparse
from application.database import db
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from application.models import *
from application.validations import NotFoundError, ValidatonError
from werkzeug.security import generate_password_hash, check_password_hash

api = Api()

# User Request Parser----------------------------------------------------------------------------------------------------------------------
new_user_req = reqparse.RequestParser()
new_user_req.add_argument('name')
new_user_req.add_argument('username')
new_user_req.add_argument('password')
new_user_req.add_argument('confirm_password')

# Post Request Parser----------------------------------------------------------------------------------------------------------------------
new_post_req = reqparse.RequestParser()
new_post_req.add_argument('title')
new_post_req.add_argument('description')
new_post_req.add_argument('img')
new_post_req.add_argument('img_name')
new_post_req.add_argument('mimetype')
new_post_req.add_argument('user_id')

# Connection Request Parser----------------------------------------------------------------------------------------------------------------------
con_req = reqparse.RequestParser()
con_req.add_argument('user_id')
con_req.add_argument('follower_id')

# Signin Request Parser----------------------------------------------------------------------------------------------------------------------
user_req = reqparse.RequestParser()
user_req.add_argument('username')
user_req.add_argument('password')

# User Output fields----------------------------------------------------------------------------------------------------------------------
user_fields = {
    "id" : fields.Integer,
    "name" : fields.String,
    "username" : fields.String,
    "password" : fields.String,
}

# Signin fields----------------------------------------------------------------------------------------------------------------------
signin_fields = {
    "username" : fields.String,
    "password" : fields.String,
}

# Post Output fields----------------------------------------------------------------------------------------------------------------------
post_fields = {
    "id" : fields.Integer,
    "title" : fields.String,
    "description" : fields.String,
    "img_name" : fields.String,
    "mimetype" : fields.String,
    "user_id" : fields.Integer,
}

# Post Output fields----------------------------------------------------------------------------------------------------------------------
con_fields = {
    "user_id" : fields.Integer,
    "follower_id" : fields.Integer,
}

# ALL User Resource-----------------------------------------------------------------------------------------------------------------------------
class Users_List(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return [user for user in users]

class User_api(Resource):
# User Resource-----------------------------------------------------------------------------------------------------------------------------
    # Get user method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(user_fields)
    def get(self,username=None):
        if username is None:
            raise ValidatonError(status_code=404,error_code="VE102",error_message="username is required")
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise ValidatonError(status_code=404,error_code="VE100",error_message="user not found")
        return user
    # Post user method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(user_fields)
    def post(self):
        data = new_user_req.parse_args()
        name = data.get('name',None)
        username = data.get('username',None)
        password = data.get('password',None)
        confirm_password = data.get('confirm_password',None)
        user = User.query.filter_by(username=username).first()
        if user:
            raise ValidatonError(status_code=404,error_code="VE107",error_message="User already exists")
        if name is None:
            raise ValidatonError(status_code=404,error_code="VE101",error_message="name is required")
        if username is None:
            raise ValidatonError(status_code=404,error_code="VE102",error_message="username is required")
        if password is None:
            raise ValidatonError(status_code=404,error_code="VE103",error_message="password is required")
        if len(password)<6:
            raise ValidatonError(status_code=404,error_code="VE104",error_message="password should be at least 6 characters")
        if confirm_password is None:
            raise ValidatonError(status_code=404,error_code="VE105",error_message="please confirm your password")
        if password!=confirm_password:
            raise ValidatonError(status_code=404,error_code="VE106",error_message="password doesn't match")
        new_user = User(name=name,username=username,password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return new_user
    # Put user method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(user_fields)
    def put(self,username=None):
        user = User.query.filter_by(username=username).first()
        data = new_user_req.parse_args()
        name = data.get('name',None)
        username = data.get('username',None)
        if user is None:
            raise ValidatonError(status_code=404,error_code="VE100",error_message="User not found")
        if name:
            user.name = name
        if username:
            user.username = username
        db.session.commit()
        return user
    # Delete user method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(user_fields)   
    def delete(self,username=None):
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise ValidatonError(status_code=404,error_code="VE102",error_message="user not found")
        db.session.delete(user)
        db.session.commit()
        return '',200

# ALL User Resource-----------------------------------------------------------------------------------------------------------------------------
class Posts_List(Resource):
    @marshal_with(post_fields)
    def get(self):
        posts = Post.query.all()
        return [post for post in posts]

# Post Resources-----------------------------------------------------------------------------------------------------------------------------
class Post_api(Resource):
    # Get post method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(post_fields)
    def get(self,title=None):
        post = Post.query.filter_by(title=title).first()
        if post is None:
            raise ValidatonError(status_code=404,error_code="VE200",error_message="Post not found")
        return post
    # Post post method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(post_fields)
    def post(self,title=None):
        data = new_post_req.parse_args()
        title = data.get('title',None)
        description = data.get('description',None)
        img = data.get('img',None)
        img_name = data.get('img_name',None)
        mimetype = data.get('mimetype',None)
        user_id = data.get('user_id',None)
        post = Post.query.filter_by(title=title).first()
        if post:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="Post already exists")
        if title is None:
            raise ValidatonError(status_code=404,error_code="VE201",error_message="Title is required")
        if description is None:
            raise ValidatonError(status_code=404,error_code="VE202",error_message="Description is required")
        new_post = Post(title=title,description=description,img=img,mimetype=mimetype,user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return new_post
    # Put post method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(post_fields)
    def put(self,title=None):
        post = Post.query.filter_by(title=title).first()
        if post is None:
            raise ValidatonError(status_code=404,error_code="VE200",error_message="Post not found")
        data = new_post_req.parse_args()
        title = data.get('title',None)
        description = data.get('description',None)
        img = data.get('img',None)
        img_name = data.get('img_name',None)
        mimetype = data.get('mimetype',None)
        if title:
            post.title = title
        if description:
            post.description = description
        if img:
            post.img = img
        if img_name:
            post.img_name = img_name
        if mimetype:
            post.mimetype = mimetype
        db.session.commit()
        return post
    # Delete post method----------------------------------------------------------------------------------------------------------------------
    @marshal_with(post_fields)   
    def delete(self,title=None):
        post = Post.query.filter_by(title=title).first()
        if post is None:
            raise ValidatonError(status_code=404,error_code="VE200",error_message="Post not found")
        db.session.delete(post)
        db.session.commit()
        return '',200

# Followers Resource-----------------------------------------------------------------------------------------------------------------------------
class Followers_List(Resource):
    @marshal_with(con_fields)
    def get(self,username=None):
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise ValidatonError(status_code=404,error_code="VE100",error_message="user not found")
        followers = Follower.query.filter_by(user_id=user.id).all()
        return [user for user in followers]
    @marshal_with(con_fields)
    def post(self,username=None):
        data = con_req.parse_args()
        user_id = data.get('user_id',None)
        follower_id = data.get('follower_id',None)
        conn = Follower.query.filter_by(user_id=user_id,follower_id=follower_id).first()
        if conn:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="Connection is already")
        if user_id is None:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="User Id is required")
        if follower_id is None:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="follower Id is required")
        new_conn = Follower(user_id=user_id,follower_id=follower_id)
        db.session.add(new_conn)
        db.session.commit()
        return new_conn
    @marshal_with(con_fields)   
    def delete(self,username=None,userid=None,followerid=None):
        conn = Follower.query.filter_by(user_id=userid,follower_id=followerid).first()
        if conn is None:
            raise ValidatonError(status_code=404,error_code="VE200",error_message="Connection not found")
        db.session.delete(conn)
        db.session.commit()
        return '',200
   
# Followins Resource-----------------------------------------------------------------------------------------------------------------------------
class Followins_List(Resource):
    @marshal_with(con_fields)
    def get(self,username=None):
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise ValidatonError(status_code=404,error_code="VE100",error_message="user not found")
        following = Follower.query.filter_by(follower_id=user.id).all()
        return [user for user in following]
    @marshal_with(con_fields)
    def post(self,username=None):
        data = con_req.parse_args()
        user_id = data.get('user_id',None)
        follower_id = data.get('follower_id',None)
        conn = Follower.query.filter_by(user_id=user_id,follower_id=follower_id).first()
        if conn:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="Connection is already")
        if user_id is None:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="User Id is required")
        if follower_id is None:
            raise ValidatonError(status_code=404,error_code="VE203",error_message="follower Id is required")
        new_conn = Follower(user_id=user_id,follower_id=follower_id)
        db.session.add(new_conn)
        db.session.commit()
        return new_conn
    @marshal_with(con_fields)   
    def delete(self,username=None,userid=None,followerid=None):
        conn = Follower.query.filter_by(user_id=userid,follower_id=followerid).first()
        if conn is None:
            raise ValidatonError(status_code=404,error_code="VE200",error_message="Connection not found")
        db.session.delete(conn)
        db.session.commit()
        return '',200

class signin(Resource):
    @marshal_with(user_fields)
    def post(self):
        data = user_req.parse_args()
        username = data.get('username',None)
        passw = data.get('password',None)
        if username is None:
            raise ValidatonError(status_code=404,error_code="VE102",error_message="username is required")
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise ValidatonError(status_code=404,error_code="VE100",error_message="user not found")
        if passw is None:
            raise ValidatonError(status_code=404,error_code="VE103",error_message="password is required")
        if len(passw)<6:
            raise ValidatonError(status_code=404,error_code="VE104",error_message="password should be at least 6 characters")
        if not check_password_hash(user.password,passw):
            raise ValidatonError(status_code=404,error_code="VE104",error_message="password does not match")
        return user

# adding endpoints to resources---------------------------------------------------------------------------------------------------------------
api.add_resource(User_api,"/user","/user/<string:username>")
api.add_resource(Post_api,"/post","/post/<string:title>")
api.add_resource(Users_List,"/users")
api.add_resource(Posts_List,"/posts")
api.add_resource(signin,"/signin")
api.add_resource(Followers_List,"/<string:username>/followers","/<string:username>/followers/<int:userid>/<int:followerid>")
api.add_resource(Followins_List,"/<string:username>/followins","/<string:username>/followins")