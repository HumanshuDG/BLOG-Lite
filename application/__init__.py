from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from application.database import db, db_init

db = SQLAlchemy()
DB_NAME = "BLOG Lite.sqlite"

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
	db.init_app(app)
	app.app_context().push()
	
	from application.models import User
	lm = LoginManager()
	lm.init_app(app)

	@lm.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	db_init(app)
	
	from .controllers import cont
	
	app.register_blueprint(cont, url_prefix='/')
	
	return app