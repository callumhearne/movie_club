import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_reviews")
def get_reviews():
    reviews = mongo.db.reviews.find()
    return render_template("reviews.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # see if username already exists in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # add the user to a session
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return render_template("profile.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if user has an account
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure it is the correct password
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return render_template("profile.html")
            else:
                # password is wrong
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # no user of that name has an account
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # gets the user's name
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    review = mongo.db.reviews.find_one({"created_by": session["user"]})

    if session["user"]:
        return render_template("profile.html", username=username,
        review=review)

    return redirect(url_for("login.html"))


@app.route("/logout")
def logout():
    # session cookie is removed so user is logged out
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        reviews = {
            "movie_name": request.form.get("movie_name"),
            "genre_name": request.form.get("genre_name"),
            "movie_review": request.form.get("movie_review"),
            "movie_rating": request.form.get("movie_rating"),
            "created_by": session["user"]
        }
        mongo.db.reviews.insert_one(reviews)
        flash("Review Successfully Created")
        return redirect(url_for("get_reviews"))

    genres = mongo.db.genres.find().sort("genre_name", 1)
    ratings = mongo.db.ratings.find().sort("rating")
    return render_template("add_review.html", genres=genres,
            ratings=ratings)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == "POST":
        reviews = {
            "movie_name": request.form.get("movie_name"),
            "genre_name": request.form.get("genre_name"),
            "movie_review": request.form.get("movie_review"),
            "movie_rating": request.form.get("movie_rating"),
            "created_by": session["user"]
        }
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, reviews)
        flash("Review Successfully Updated")

    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})

    genres = mongo.db.genres.find().sort("genre_name", 1)
    ratings = mongo.db.ratings.find().sort("rating")
    return render_template("edit_review.html", review=review, genres=genres,
        ratings=ratings)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_reviews"))


@app.route("/get_genres")
def get_genres():
    genres = list(mongo.db.genres.find().sort("genre_name", 1))
    return render_template("genres.html", genres=genres)


@app.route("/genre", methods=["GET", "POST"])
def add_genre():
    if request.method == "POST":

        existing_genre = mongo.db.genres.find_one(
            {"genre_name": request.form.get("genre_name").lower()})

        if existing_genre:
            flash("Genre already exists")
            return redirect(url_for("add_genre.html"))

        genre = {
            "genre_name": request.form.get("genre_name")
        }
        mongo.db.genres.insert_one(genre)
        flash("New Genre Added")
        return redirect(url_for("get_genres"))

    return render_template("add_genre.html")


@app.route("/edit_genre/<genre_id>", methods=["GET", "POST"])
def edit_genre(genre_id):
    if request.method == "POST":
        submit = {
            "genre_name": request.form.get("genre_name")
        }
        mongo.db.genres.update({"_id": ObjectId(genre_id)}, submit)
        flash("Genre Successfully Updated")
        return redirect(url_for("get_genres"))

    genre = mongo.db.genres.find_one({"_id": ObjectId(genre_id)})
    return render_template("edit_genre.html", genre=genre)


@app.route("/delete_genre/<genre_id>")
def delete_genre(genre_id):
    mongo.db.genres.remove({"_id": ObjectId(genre_id)})
    flash("Genre Successfully Deleted")
    return redirect(url_for("get_genres"))


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    reviews = list(mongo.db.reviews.find({"$text": {"$search": query}}))
    return render_template("reviews.html", reviews=reviews)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
