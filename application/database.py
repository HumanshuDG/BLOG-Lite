from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

engine = None
Base = declarative_base()
db = SQLAlchemy()

def db_init(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()