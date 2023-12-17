from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# class Book(db.Model):
#     __tablename__ = "books"
#     isbn = db.Column(db.String, primary_key = True)
#     title = db.Column(db.String, nullable = False)
#     author = db.Column(db.String, nullable = False)
#     year = db.Column(db.String, nullable = False)


class User(db.Model):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)

class Ticker(db.Model):
    
    __tablename__ = "fav_tickers"
    id = db.Column(db.Integer, primary_key = True)
    creator = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    name = db.Column(db.String, nullable = False)
    nominator = db.Column(db.String, nullable = False)
    denominator = db.Column(db.String, nullable = False)
    bars_back = db.Column(db.Integer, nullable = False)
    interval = db.Column(db.String, nullable = False)




# class Review(db.Model):

#     __tablename__ = "reviews"
#     id = db.Column(db.Integer, primary_key = True)
#     userid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
#     book_isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable = False)
#     review = db.Column(db.Integer, nullable = False)