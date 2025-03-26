from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, TextAreaField, SubmitField
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)
os.getenv('app.secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app) 

def configure():
    load_dotenv()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

def get_movie(movie_name):
    movie_data = requests.get(f'http://www.omdbapi.com/?t={movie_name}&apikey={os.getenv('api_key')}')
    response = movie_data.json()
    if response.get("Response") == "True":
        return response.get("Title"), response.get("Released"), response.get("Rated"), response.get('Director'), response.get('Actors'), response.get('imdbRating'), response.get('Genre'), response.get('Writer'), response.get('Poster')
    else:
        return None, None, None, None, None, None, None, None, None

@app.route("/", methods=["GET", "POST"])
def index():
    title = None
    release_date = None
    rating = None
    director = None
    actors = None
    imdbRating = None
    Genre = None
    Writers = None
    Poster = None
    if request.method == "POST":
        movie_name = request.form.get("movie_name")
        title, release_date, rating, director, actors, imdbRating, Genre, Writers, Poster = get_movie(movie_name) 
    return render_template("movie.html", title=title, release_date=release_date, rating=rating, director=director, actors=actors, imdbRating=imdbRating, Genre=Genre, Writers=Writers, Poster=Poster)


@app.route("/make-post", methods=['GET', 'POST'])
def make_post():
    form = PostForm()
    post = None
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        print('Hi')
        return redirect(url_for('posts'))
    else:
        print('No')
    return render_template('make_post.html', form=form, post=post)

@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    try: 
        db.session.delete(post_to_delete)
        db.session.commit()
        posts = Post.query.all()
        return render_template('posts.html', posts = posts, title=Post.title, content=Post.content)
    except:
        posts = Post.query.all()
        return render_template('posts.html', posts = posts, title=Post.title, content=Post.content)


@app.route("/posts")
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts = posts, title=Post.title, content=Post.content)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=80)