from flask import Flask, render_template, request
import sqlite3
from my_website import ml_model
from collections import Counter

app = Flask(__name__)

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        mood TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        mood TEXT,
        rating INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# AI LOGIC
# =========================
def generate_sections(question, mood):
    q = question.lower()

    if "exam" in q:
        return {
            "overview": "Exam stress is common and manageable.",
            "options": "Better planning and focus techniques.",
            "pros_cons": "Pros: clarity. Cons: discipline required.",
            "next_steps": "Make a 7-day revision plan."
        }

    if "career" in q or "future" in q:
        return {
            "overview": "Career confusion means you care about your future.",
            "options": "Explore interests, skills, and exposure.",
            "pros_cons": "Pros: clarity. Cons: takes time.",
            "next_steps": "Shortlist two paths."
        }

    return {
        "overview": "This is a thoughtful question.",
        "options": "Break it into smaller steps.",
        "pros_cons": "Pros: less stress. Cons: slower progress.",
        "next_steps": "Take one action today."
    }

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    mood = request.form["mood"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memory (question, mood) VALUES (?, ?)",
        (question, mood)
    )
    conn.commit()
    conn.close()

    sections = generate_sections(question, mood)
    confidence = ml_model.predict_quality(question)

    return render_template(
        "answer.html",
        question=question,
        mood=mood,
        sections=sections,
        confidence=confidence
    )


@app.route("/feedback", methods=["POST"])
def feedback():
    rating = int(request.form["rating"])
    question = request.form["question"]
    mood = request.form["mood"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedback (question, mood, rating) VALUES (?, ?, ?)",
        (question, mood, rating)
    )
    conn.commit()
    conn.close()

    ml_model.train_model()
    return "Feedback saved"


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT rating FROM feedback")
    ratings = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT mood FROM memory")
    moods = [m[0] for m in cur.fetchall()]

    cur.execute("SELECT question FROM memory ORDER BY id DESC LIMIT 10")
    questions = [q[0] for q in cur.fetchall()]

    conn.close()

    feedback_counts = [
        ratings.count(5),
        ratings.count(3),
        ratings.count(1)
    ]

    mood_counts = dict(Counter(moods))

    return render_template(
        "admin.html",
        feedback=feedback_counts,
        moods=mood_counts,
        questions=questions
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
