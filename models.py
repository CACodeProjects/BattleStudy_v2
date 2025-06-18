from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    xp = db.Column(db.Integer, default=0)

    # Relationship to track this user's question progress
    question_progress = db.relationship("QuestionProgress", backref="user", lazy=True)


class QuestionProgress(db.Model):
    __tablename__ = "question_progress"
    id = db.Column(db.Integer, primary_key=True)

    # Links progress to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # The unique question ID string (e.g., 1.1.1-Security-Controls_12)
    question_id = db.Column(db.String, nullable=False)

    # Cooldown counter (0 means eligible to show again)
    cooldown = db.Column(db.Integer, default=0)

    # Mistake counter for adaptive difficulty
    mistakes = db.Column(db.Integer, default=0)

    # Difficulty level of this question for this user
    difficulty_level = db.Column(db.Integer, default=1)

    # The "chapter" or "world" this question belongs to
    chapter = db.Column(db.String, nullable=True)

    # ✅ NEW FIELD: Tracks whether this question has been successfully completed
    completed = db.Column(db.Boolean, default=False)
