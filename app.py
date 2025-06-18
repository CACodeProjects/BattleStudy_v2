from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, QuestionProgress
from dotenv import load_dotenv
from pathlib import Path
import json
import random
import socket
import os

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = "secret"
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

# Load all questions
QUESTIONS_FILE = Path("data/Questions_Scenario_Based_v4.json")
with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    all_questions = json.load(f)

# API endpoint to get questions
@app.route("/api/questions", methods=["GET"])
def get_questions():
    limit = int(request.args.get("limit", 10))
    chapter = request.args.get("chapter")
    questions = [q for q in all_questions if chapter is None or q.get("chapter") == chapter]
    return jsonify(questions[:limit])

# Index/login route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        session["username"] = username

        # Reset session for new login
        session["player_hp"] = 100
        session["wizard_hp"] = 100
        session["streak"] = 0
        session.pop("last_result", None)
        session.pop("question", None)
        session.pop("world", None)

        # Create or retrieve user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, email=f"{username}@example.com")
            db.session.add(user)
            db.session.commit()
            flash(f"Welcome, {username}!")
        else:
            flash(f"Welcome back, {username}!")

        return redirect(url_for("choose_world"))
    return render_template("index.html")

# World selection screen
@app.route("/choose-world", methods=["GET", "POST"])
def choose_world():
    chapters = sorted({q.get("chapter", "Mixed") for q in all_questions})

    if request.method == "POST":
        session["world"] = request.form["world"]

        # Reset HP if the previous battle ended
        if session.get("player_hp", 100) <= 0 or session.get("wizard_hp", 100) <= 0:
            session["player_hp"] = 100
            session["wizard_hp"] = 100
            session["streak"] = 0
            session.pop("final_player_hp", None)
            session.pop("final_wizard_hp", None)

        session.pop("last_result", None)

        return redirect(url_for("battle"))

    battle_active = (
        session.get("player_hp", 100) > 0 and session.get("wizard_hp", 100) > 0
    )

    return render_template(
        "choose_world.html",
        chapters=chapters,
        player_hp=session.get("player_hp", 100),
        wizard_hp=session.get("wizard_hp", 100),
        streak=session.get("streak", 0),
        battle_active=battle_active
    )

# Main battle logic
@app.route("/battle", methods=["GET", "POST"])
def battle():
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    world = session.get("world", "ALL")

    # Ensure HP values are initialized
    session["player_hp"] = session.get("player_hp", 100)
    session["wizard_hp"] = session.get("wizard_hp", 100)
    session["streak"] = session.get("streak", 0)

    # Clear final HP display if battle still active
    if session["player_hp"] > 0:
        session.pop("final_player_hp", None)
    if session["wizard_hp"] > 0:
        session.pop("final_wizard_hp", None)

    progresses = {str(p.question_id): p for p in user.question_progress}

    # POST: handle answer submission
    if request.method == "POST":
        # Decrease cooldowns
        for p in progresses.values():
            if p.cooldown > 0:
                p.cooldown -= 1
        db.session.commit()

        qid = request.form["qid"]
        user_answer = request.form["answer"]
        world = request.form["world"]

        question = session.get("question")

        if not question or str(question["id"]) != qid:
            flash("Question mismatch — please try again.")
            return redirect(url_for("battle"))

        correct_answer = question.get("correct_answer", "")
        correct_letter = correct_answer[0].upper() if correct_answer else ""

        # Get or create question progress
        qid_str = str(qid)
        progress = progresses.get(qid_str)

        if not progress:
            progress = QuestionProgress(user_id=user.id, question_id=qid_str, difficulty_level=1)
            db.session.add(progress)
            db.session.commit()
            progresses[qid_str] = progress

        # Scoring logic
        difficulty = progress.difficulty_level or 1
        is_correct = user_answer.strip().upper() == correct_letter

        damage_config = {
            "player_damage": {1: 10, 2: 15, 3: 25},
            "wizard_damage": {1: 10, 2: 15, 3: 25},
        }
        dmg_to_wizard = damage_config["wizard_damage"][difficulty]
        dmg_to_player = damage_config["player_damage"][difficulty]

        if is_correct:
            session["wizard_hp"] -= dmg_to_wizard
            user.xp += 10
            session["streak"] += 1
            result = f"Correct! You hit the wizard for {dmg_to_wizard} damage."
            progress.cooldown = 3
            progress.mistakes = 0
            if progress.difficulty_level > 1:
                progress.difficulty_level -= 1
        else:
            session["player_hp"] -= dmg_to_player
            session["streak"] = 0
            result = f"❌ Wrong! The wizard hit you for {dmg_to_player} damage.<br>Correct answer: {correct_answer}"
            progress.cooldown = 1
            progress.mistakes += 1
            progress.difficulty_level = min(difficulty + 1, 3)

        # Handle battle end
        if session["wizard_hp"] <= 0:
            session["final_player_hp"] = session["player_hp"]
            session["final_wizard_hp"] = 0
            session["wizard_hp"] = 0
            session["player_hp"] = 0
            result += "<br>🏆 You defeated the wizard! +50 XP"
            user.xp += 50
        elif session["player_hp"] <= 0:
            session["final_player_hp"] = 0
            session["final_wizard_hp"] = session["wizard_hp"]
            session["player_hp"] = 0
            result += "<br>💀 You were defeated by the wizard."

        db.session.commit()
        session["last_result"] = result
        return redirect(url_for("battle"))

    # GET: show new question and game state
    last_result = session.pop("last_result", None)

    question_ids_on_cooldown = {str(p.question_id) for p in progresses.values() if p.cooldown > 0}

    usable_questions = [
        q for q in all_questions
        if (world == "ALL" or q.get("chapter") == world)
        and str(q["id"]) not in question_ids_on_cooldown
    ]

    if not usable_questions:
        return render_template(
            "battle.html",
            username=username,
            world=world,
            profile=user,
            difficulty=0,
            mistakes=0,
            question=None,
            error_message=f"No available questions in {world}.",
            result=last_result,
            questions_answered=0,
            total_questions=0,
        )

    question = random.choice(usable_questions)
    qid = str(question["id"])
    progress = progresses.get(qid, QuestionProgress())
    difficulty = progress.difficulty_level or 1
    mistakes = progress.mistakes

    session["question"] = question

    # Progress tracking
    world_questions = [q for q in all_questions if world == "ALL" or q.get("chapter") == world]
    total_questions = len(world_questions)

    answered_ids = {
        str(p.question_id)
        for p in progresses.values()
        if p.cooldown > 0 and str(p.question_id) != qid
    }
    answered_questions = [q for q in world_questions if str(q["id"]) in answered_ids]
    questions_answered = len(answered_questions)

    return render_template(
        "battle.html",
        username=username,
        world=world,
        question=question,
        profile=user,
        difficulty=difficulty,
        mistakes=mistakes,
        result=last_result,
        questions_answered=questions_answered,
        total_questions=total_questions,
    )

# Restart current battle
@app.route("/restart", methods=["POST"])
def restart_battle():
    session["player_hp"] = 100
    session["wizard_hp"] = 100
    session["streak"] = 0
    session.pop("last_result", None)
    return redirect(url_for("battle"))

# Run Flask server
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    host_ip = socket.gethostbyname(socket.gethostname())
    print(f"Local network access: http://{host_ip}:5000")
    print("Access on this machine: http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
