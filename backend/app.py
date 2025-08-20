import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from db import engine, SessionLocal, Base
from models import Internship
from verify import verify_internship, seed_default_patterns

load_dotenv()

app = Flask(__name__)
CORS(app)

# Create tables at startup
with engine.begin() as conn:
    Base.metadata.create_all(bind=conn)

# Seed scam patterns if empty
with SessionLocal() as db:
    seed_default_patterns(db)

@app.get("/")
def home():
    return jsonify({"message": "Backend is running ✅"})

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "internship-credibility-backend"})

@app.post("/check")
def check():
    data = request.get_json(silent=True) or {}
    with SessionLocal() as db:
        result = verify_internship(data, db)
        # best-effort persistence
        try:
            item = Internship(
                title=data.get("title"),
                company_name=data.get("company_name"),
                description=data.get("description"),
                link=data.get("link"),
                email=data.get("email"),
                is_paid=result["paid"],
                credibility_score=result["credibility"],
                status=result["status"],
            )
            db.add(item)
            db.commit()
        except Exception as e:
            print("Persist error:", e)
    return jsonify(result), 200

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
