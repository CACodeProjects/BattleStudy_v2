
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    has_logged_in_before = db.Column(db.Boolean, default=False)
    question_progress = db.relationship("QuestionProgress", backref="user", lazy=True)

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    choice_a = db.Column(db.String, nullable=True)
    choice_b = db.Column(db.String, nullable=True)
    choice_c = db.Column(db.String, nullable=True)
    choice_d = db.Column(db.String, nullable=True)
    correct_answer = db.Column(db.String, nullable=False)
    chapter = db.Column(db.String, nullable=True)
    explanation = db.Column(db.Text, nullable=True)
    tags = db.Column(db.ARRAY(db.String), nullable=True)
    type = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "choice_a": self.choice_a,
            "choice_b": self.choice_b,
            "choice_c": self.choice_c,
            "choice_d": self.choice_d,
            "correct_answer": self.correct_answer,
            "chapter": self.chapter,
            "explanation": self.explanation,
            "tags": self.tags,
            "type": self.type
        }

class QuestionProgress(db.Model):
    __tablename__ = "question_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.String, nullable=False)  # <-- changed from Integer
    cooldown = db.Column(db.Integer, default=0)
    mistakes = db.Column(db.Integer, default=0)
    difficulty_level = db.Column(db.Integer, default=1)

