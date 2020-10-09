
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


win= sys.platform.startswith('win')
if win:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY",'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATABASE_FILE','data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

#实例化Flask-Longin扩展类
login_manager = LoginManager(app)
login_manager.login_view = 'login' #对视图保护的情况，把非认证用户重定向到login.html
login_manager.login_message = '请登录后再访问' #认证保护的错误提示

@login_manager.user_loader
def load_user(user_id):#创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id)) #用ID作为User模型的主键查询对应的用户
    return user #返回用户对象

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user = user) 

from watchlist import views,errors,commands
from watchlist.models import User,Movie