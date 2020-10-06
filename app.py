from flask import Flask,render_template

app = Flask(__name__)

name = 'CrazyLMX'
movies = [
    {'title':'龙猫','year':'1988'},
    {'title':'霸王别姬','year':'1982'},
    {'title':'天下无贼','year':'1988'},
    {'title':'阿凡达','year':'2008'},
]


@app.route('/')
def index():
    return render_template('index.html',name = name ,movies = movies)

if __name__ == "__main__":
    app.run()