from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie

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
        flash('Item created.')
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
        flash("Invalid username or password.")
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
            return redirect(url_for('settings'))
        
        current_user.name = name # 把当前登录对象的name属性替换成form提交的属性
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    
    return render_template('settings.html')