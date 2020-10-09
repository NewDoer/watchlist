from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db


class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key = True ) 
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    #设置密码，接收参数
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    #验证密码，接收密码参数
    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer,primary_key = True ) 
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))