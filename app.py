from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, TextAreaField, SubmitField
import requests
import key_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'SECRET_KEY'
db = SQLAlchemy(app)
key_file.SECRET_KEY  

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    review = db.Column(db.Text, nullable=False)

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    review = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Post')

def get_movie(movie_name):
    movie_data = requests.get(f'http://www.omdbapi.com/?t={movie_name}&apikey={key_file.api_key}')
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


@app.route("/make-review", methods=['GET', 'POST'])
def make_review():
    form = PostForm()
    review = None
    if form.validate_on_submit():
        review = Post(title=form.title.data, review=form.review.data)
        db.session.add(review)
        db.session.commit()
        print('Hi')
        return redirect(url_for('reviews'))
    else:
        print('No')
    return render_template('make_review.html', form=form, review=review)

@app.route('/reviews/delete/<int:id>')
def delete_review(id):
    review_delete = Post.query.get_or_404(id)
    try: 
        db.session.delete(review_delete)
        db.session.commit()
        reviews = Post.query.all()
        return render_template('reviews.html', reviews = reviews, title=Post.title, review=Post.review)
    except:
        reviews = Post.query.all()
        return render_template('reviews.html', reviews = reviews, title=Post.title, review=Post.review)


@app.route("/reviews")
def reviews():
    reviews = Post.query.all()
    return render_template('reviews.html', reviews = reviews, title=Post.title, review=Post.review)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=80)