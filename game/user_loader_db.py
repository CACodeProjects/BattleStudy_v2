from game.db import db, User  # or from app import db, User if using a single file

def load_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, xp=0, streak=0, question_progress={})
        db.session.add(user)
        db.session.commit()
    return {
        "username": user.username,
        "xp": user.xp,
        "streak": user.streak,
        "question_progress": user.question_progress or {}
    }

def save_user(profile):
    user = User.query.filter_by(username=profile["username"]).first()
    if user:
        user.xp = profile["xp"]
        user.streak = profile["streak"]
        user.question_progress = profile["question_progress"]
        db.session.commit()
