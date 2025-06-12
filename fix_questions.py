import json
from models import db, Question
from app import app

with app.app_context():
    print("Clearing existing questions...")
    Question.query.delete()
    db.session.commit()

    with open("data/Questions_Scenario_Based_v2.json", "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    print(f"Loading {len(questions_data)} questions...")
    for q in questions_data:
        question = Question(
            question=q["question"],
            choice_a=q.get("choice_a"),
            choice_b=q.get("choice_b"),
            choice_c=q.get("choice_c"),
            choice_d=q.get("choice_d"),
            correct_answer=q["correct_answer"],
            chapter=q.get("chapter"),
            explanation=q.get("explanation"),
            tags=q.get("tags"),
            type=q.get("type"),
        )
        db.session.add(question)

    db.session.commit()
    print("? Question table successfully refreshed.")

