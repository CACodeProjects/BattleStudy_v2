import json
from models import db, Question
from app import app

# Load questions from file
with open("data/Questions_Scenario_Based_v2.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

with app.app_context():
    for q in questions:
        choices = q.get("options", [])
        if not db.session.get(Question, q["id"]):
            question = Question(
                id=q["id"],
                question=q.get("question", ""),
                choice_a=choices[0] if len(choices) > 0 else None,
                choice_b=choices[1] if len(choices) > 1 else None,
                choice_c=choices[2] if len(choices) > 2 else None,
                choice_d=choices[3] if len(choices) > 3 else None,
                correct_answer=q.get("correct_answer", [None])[0],
                chapter=q.get("chapter", "Unknown"),
                explanation=q.get("explanation", ""),
                tags=q.get("tags", ""),
                type=q.get("type", "")
            )
            db.session.add(question)
    db.session.commit()
    print(f"✅ Populated {len(questions)} questions into the database.")
