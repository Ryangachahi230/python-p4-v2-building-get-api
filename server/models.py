# server/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -------------------
# MODELS
# -------------------

class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    genre = db.Column(db.String, nullable=False)
    platform = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    reviews = db.relationship("Review", back_populates="game", cascade="all, delete-orphan")

    def to_dict(self, include_reviews=False):
        """Explicit serializer with optional reviews."""
        data = {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "platform": self.platform,
            "price": self.price,
        }
        if include_reviews:
            data["reviews"] = [review.to_dict(include_user=True) for review in self.reviews]
        return data


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)

    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String)

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    game = db.relationship("Game", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    def to_dict(self, include_user=False):
        data = {
            "id": self.id,
            "score": self.score,
            "comment": self.comment,
        }
        if include_user:
            data["user"] = self.user.to_dict()
        return data
