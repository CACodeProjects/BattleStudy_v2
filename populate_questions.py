from dotenv import load_dotenv
import os
import json
from app import app, db
from models import Question

load_dotenv()

with app.app_context():
    with open("E:/VibeCode/Wizard_battle_web/data/Questions_Scenario_Based_v2.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    count = 0
    for q in questions:
        # Use question text to check for duplicates instead of ID
        existing = Question.query.filter_by(question=q["question"]).first()
        if not existing:
            new_question = Question(
                question=q["question"],
                choice_a=q.get("choice_a"),
                choice_b=q.get("choice_b"),
                choice_c=q.get("choice_c"),
                choice_d=q.get("choice_d"),
                correct_answer=q.get("correct_answer"),
                chapter=q.get("chapter", ""),
                explanation=q.get("explanation", ""),
                tags=q.get("tags", []),
                type=q.get("type", "")
            )
            db.session.add(new_question)
            count += 1

    db.session.commit()
    print(f"? Inserted {count} new questions.")
