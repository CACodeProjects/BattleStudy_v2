from app import app, db
from models import Question
import json

with app.app_context():
    with open("E:\VibeCode\Wizard_battle_web\data\Questions_Scenario_Based_v2.json", "r") as f:
        questions = json.load(f)

    for q in questions:
        question = Question(
            question=q["question"],
            choice_a=q.get("choice_a"),
            choice_b=q.get("choice_b"),
            choice_c=q.get("choice_c"),
            choice_d=q.get("choice_d"),
            correct_answer=q["correct_answer"],
            chapter=q.get("chapter", ""),
            explanation=q.get("explanation", ""),
            tags=q.get("tags", []),
            type=q.get("type", "")
        )
        db.session.add(question)

    db.session.commit()
    print(f"{len(questions)} questions added.")
