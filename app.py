# 🔙️ Updated app.py — Final Fix: Accurate Question Completion Filtering + Cooldown Handling

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from models import db, User, QuestionProgress
from dotenv import load_dotenv
from pathlib import Path
import json
import random
import socket
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///default.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

QUESTIONS_FILE = Path("data/Questions_Scenario_Based_v5.json")
with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    all_questions = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()

        if not username:
            flash("Please enter a valid username.")
            return redirect(url_for("index"))

        session["username"] = username
        session["player_hp"] = 100
        session["wizard_hp"] = 100
        session["streak"] = 0
        session.pop("last_result", None)
        session.pop("question", None)
        session.pop("world", None)

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, email=f"{username}@example.com")
            db.session.add(user)
            db.session.commit()

        return redirect(url_for("choose_world"))
    return render_template("index.html")

@app.route("/choose-world", methods=["GET", "POST"])
def choose_world():
    chapters = sorted({q.get("chapter", "Mixed") for q in all_questions})
    if request.method == "POST":
        session["world"] = request.form["world"]
        if session.get("player_hp", 100) <= 0 or session.get("wizard_hp", 100) <= 0:
            session["player_hp"] = 100
            session["wizard_hp"] = 100
            session["streak"] = 0
            session.pop("final_player_hp", None)
            session.pop("final_wizard_hp", None)
        session.pop("last_result", None)
        return redirect(url_for("battle"))

    battle_active = session.get("player_hp", 100) > 0 and session.get("wizard_hp", 100) > 0
    return render_template(
        "choose_world.html",
        chapters=chapters,
        player_hp=session.get("player_hp", 100),
        wizard_hp=session.get("wizard_hp", 100),
        streak=session.get("streak", 0),
        battle_active=battle_active
    )

@app.route("/battle", methods=["GET", "POST"])
def battle():
    username = session.get("username")
    if not username:
        flash("Please enter your username to start a battle.")
        return redirect(url_for("index"))

    user = User.query.filter_by(username=username).first()
    if not user:
        session.clear()
        flash("Your session expired. Please sign in again.")
        return redirect(url_for("index"))

    world = session.get("world", "ALL")

    session["player_hp"] = session.get("player_hp", 100)
    session["wizard_hp"] = session.get("wizard_hp", 100)
    session["streak"] = session.get("streak", 0)

    if session["player_hp"] > 0:
        session.pop("final_player_hp", None)
    if session["wizard_hp"] > 0:
        session.pop("final_wizard_hp", None)

    progresses = {str(p.question_id): p for p in user.question_progress}

    if request.method == "POST":
        qid = request.form["qid"]
        user_answer = request.form["answer"]
        world = request.form["world"]

        question = session.get("question")
        if not question or str(question["id"]) != qid:
            flash("Question mismatch — please try again.")
            return redirect(url_for("battle"))

        correct_answer = question.get("correct_answer", "")
        correct_letter = correct_answer[0].upper() if correct_answer else ""

        qid_str = str(qid)
        progress = progresses.get(qid_str)
        if not progress:
            chapter = next((q.get("chapter") for q in all_questions if str(q["id"]) == qid_str), "Unknown")
            progress = QuestionProgress(
                user_id=user.id,
                question_id=qid_str,
                chapter=chapter,
                difficulty_level=1
            )
            db.session.add(progress)
            db.session.commit()
            progresses[qid_str] = progress

        difficulty = progress.difficulty_level or 1
        is_correct = user_answer.strip().upper() == correct_letter

        damage_config = {
            "player_damage": {1: 10, 2: 15, 3: 25},
            "wizard_damage": {1: 10, 2: 15, 3: 25},
        }
        dmg_to_wizard = damage_config["wizard_damage"][difficulty]
        dmg_to_player = damage_config["player_damage"][difficulty]

        world_questions = [q for q in all_questions if world == "ALL" or q.get("chapter") == world]
        total_questions = len(world_questions)

        if is_correct:
            session["wizard_hp"] -= dmg_to_wizard
            user.xp += 10
            session["streak"] += 1
            result = f"Correct! You hit the wizard for {dmg_to_wizard} damage."
            progress.cooldown = total_questions + 1
            progress.completed = True
            progress.mistakes = 0
            if progress.difficulty_level > 1:
                progress.difficulty_level -= 1
        else:
            session["player_hp"] -= dmg_to_player
            session["streak"] = 0
            result = f"❌ Wrong! The wizard hit you for {dmg_to_player} damage.\nCorrect answer: {correct_answer}"
            progress.cooldown = 1
            progress.completed = False
            progress.mistakes += 1
            progress.difficulty_level = min(difficulty + 1, 3)

        # Decrease cooldowns only for questions that were NOT just answered
        for p in user.question_progress:
            if str(p.question_id) != qid_str and p.cooldown > 0:
                p.cooldown -= 1

        if session["wizard_hp"] <= 0:
            session["final_player_hp"] = session["player_hp"]
            session["final_wizard_hp"] = 0
            session["wizard_hp"] = 0
            session["player_hp"] = 0
            result += "\n🏆 You defeated the wizard! +50 XP"
            user.xp += 50
        elif session["player_hp"] <= 0:
            session["final_player_hp"] = 0
            session["final_wizard_hp"] = session["wizard_hp"]
            session["player_hp"] = 0
            result += "\n💀 You were defeated by the wizard."

        db.session.commit()
        session["last_result"] = result
        return redirect(url_for("battle"))

    # GET logic continues here
    last_result = session.pop("last_result", None)

    # ✅ More accurate filtering for usable questions
    usable_questions = []
    for q in all_questions:
        if world != "ALL" and q.get("chapter") != world:
            continue  # skip if not in selected world

        qid = str(q["id"])
        progress = progresses.get(qid)

        if not progress:
            usable_questions.append(q)  # never seen → usable
        elif progress.completed is False and progress.cooldown == 0:
            usable_questions.append(q)  # not completed + cooldown expired → usable

    # Calculate progress before possibly rendering "no questions left"
    world_questions = [q for q in all_questions if world == "ALL" or q.get("chapter") == world]
    total_questions = len(world_questions)
    world_question_ids = {str(q["id"]) for q in world_questions}

    answered_ids = {
        str(p.question_id)
        for p in user.question_progress
        if p.completed and (p.chapter == world or world == "ALL")
    }
    questions_answered = len(world_question_ids & answered_ids)


    # 🔁 FIXED: check AFTER the loop, not inside it
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
            questions_answered=questions_answered,
            total_questions=total_questions
        )


    question = random.choice(usable_questions)
    qid = str(question["id"])
    progress = progresses.get(qid)

    difficulty = progress.difficulty_level if progress else 1
    mistakes = progress.mistakes if progress else 0
    session["question"] = question

    print("Current qid:", qid)
    print("Questions Answered:", questions_answered)
    print("Total Questions in world:", len(world_question_ids))
    print("🧪 DEBUG — Correct Answer:", question.get("correct_answer", "N/A"))

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
        total_questions=len(world_question_ids)
    )


@app.route("/restart", methods=["POST"])
def restart_battle():
    session["player_hp"] = 100
    session["wizard_hp"] = 100
    session["streak"] = 0
    session.pop("last_result", None)
    return redirect(url_for("battle"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    host_ip = socket.gethostbyname(socket.gethostname())
    print(f"Local network access: http://{host_ip}:5000")
    print("Access on this machine: http://127.0.0.1:5000")
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        host="0.0.0.0",
        port=5000,
    )
