# server/app.py
from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from models import db, Game, User, Review

app = Flask(__name__)

# -------------------
# CONFIG
# -------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# -------------------
# HELPERS
# -------------------
def not_found(message="Resource not found"):
    return jsonify({"error": message}), 404

def bad_request(message="Bad request"):
    return jsonify({"error": message}), 400


# -------------------
# ROUTES
# -------------------

@app.route("/games", methods=["GET"])
def games():
    """Paginated list of games."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Game.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "games": [g.to_dict() for g in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
    })


@app.route("/games/<int:id>", methods=["GET"])
def game_by_id(id):
    """Get single game with reviews."""
    game = Game.query.filter_by(id=id).first()
    if not game:
        return not_found(f"Game with id {id} not found")
    return jsonify(game.to_dict(include_reviews=True))


@app.route("/games/<int:id>/users", methods=["GET"])
def game_users(id):
    """Get users who reviewed a game."""
    game = Game.query.filter_by(id=id).first()
    if not game:
        return not_found(f"Game with id {id} not found")
    users = [review.user.to_dict() for review in game.reviews]
    return jsonify(users)


@app.route("/reviews", methods=["POST"])
def create_review():
    """Add a review for a game by a user."""
    data = request.get_json()
    if not data or "game_id" not in data or "user_id" not in data or "score" not in data:
        return bad_request("Missing required fields: game_id, user_id, score")

    game = Game.query.get(data["game_id"])
    user = User.query.get(data["user_id"])
    if not game or not user:
        return not_found("Invalid game_id or user_id")

    review = Review(
        score=data["score"],
        comment=data.get("comment"),
        game=game,
        user=user
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(review.to_dict(include_user=True)), 201


# -------------------
# ENTRYPOINT
# -------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
