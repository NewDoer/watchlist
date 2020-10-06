from os import name, truncate
from flask import Flask,render_template
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



@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',user = user ,movies = movies)

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


if __name__ == "__main__":
    app.run()