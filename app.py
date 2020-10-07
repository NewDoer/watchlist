from os import name, truncate
from flask import Flask,render_template,redirect,flash,request,url_for
from flask_sqlalchemy import SQLAlchemy
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


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key = True ) 
    name = db.Column(db.String(20))

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer,primary_key = True ) 
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
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
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

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