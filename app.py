from os import name, truncate
from flask import Flask,render_template,redirect,flash,request,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_required,current_user,login_user,logout_user,UserMixin

import click
import os
import sys


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
app.secret_key = "aaaxxx"
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
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


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated: #判断当前用户是否认证
            return redirect(url_for('index')) #未认证就重定向走
        title = request.form.get('title')
        year = request.form.get('year')
        
        if not title or not year or len(year)>4 or len(title) > 60:
            flash("Invalid input")
            return redirect(url_for('index'))
        
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item creatd.')
        return redirect(url_for('index'))
    
    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',movies = movies)

@app.route('/movie/edit/<int:movie_id>',methods = ['GET','POST'])
@login_required #视图保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input')
            return(redirect(url_for('edit',movie_id = movie_id)))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash("Item updated.")
        return redirect(url_for('index'))
    
    return render_template('edit.html',movie=movie)

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required #视图保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

@app.route('/login',methods= ['GET','POST'])
def login():
    if request.method =='POST':
        #读出浏览器传过来的表单数据
        username = request.form['username']
        password = request.form['password']
        
        #验证数据是否为空
        if not username or not password:
            flash("Invalid input")
            return redirect(url_for('login'))
        
        #读取数据模型第一条数据
        user = User.query.first()
        
        #验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) #登录用户
            flash('Login success')
            return redirect(url_for('index'))
        flash('错误的用户名或密码')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required #视图保护，非认证用户不能访问
def logout():
    logout_user()
    flash("Goodbye")
    return redirect(url_for('index'))

@app.route('/settings',methods=["GET","POST"])
@login_required #视图保护，非认证用户不能访问
def settings():
    if request.method == "POST":
        name = request.form.get('name')
        print(name)
        flash(name)
        if not name or len(name) >20:
            flash('Invalid input.')
        
        current_user.name = name # 把当前登录对象的name属性替换成form提交的属性
        db.session.commit()
        flash('Settings updates.')
        return redirect(url_for('index'))
    
    return render_template('settings.html')



@app.cli.command()
def forge():
    db.create_all()

    name = 'CrazyLMX'
    movies = [
        {'title':'龙猫','year':'1988'},
        {'title':'霸王别姬','year':'1982'},
        {'title':'天下无贼','year':'1988'},
        {'title':'阿凡达','year':'2008'},
    ]

    user = User(name = name )
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')


@app.cli.command()
@click.option('--drop',is_flag=True,help="Create after drop.")
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initalized database.")

@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help="The password used to login.")
def admin(username,password):

    db.create_all()

    user=User.query.first()
    if user is not None:
        click.echo('Updating user...') 
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username,name="Admin")
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')

@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user = user) 

if __name__ == "__main__":
    app.run()