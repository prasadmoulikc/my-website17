from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-key"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        stage TEXT,
        problem TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- SMART DECISION LOGIC ----------
def decision_engine(stage, text):
    text = text.lower()

    risk = 0
    urgency = 0
    clarity = 5

    danger_words = ["loan", "fees", "money", "pay", "quick", "fast", "guarantee"]
    confusion_words = ["confused", "lost", "scared", "panic", "dont know"]

    for w in danger_words:
        if w in text:
            risk += 2
            urgency += 1

    for w in confusion_words:
        if w in text:
            clarity -= 2

    if "degree" in text and "skill" in text:
        return (
            "Balanced Path Recommended",
            "You are stuck between degree and skills. Both matter, timing matters more.",
            [
                "Continue your education if already enrolled",
                "Start ONE practical skill alongside",
                "Avoid expensive courses now",
                "Review after 30 days"
            ]
        )

    if clarity <= 1:
        return (
            "Pause & Simplify",
            "Your mind is overloaded. You need clarity, not pressure.",
            [
                "Stop consuming random advice",
                "Pick ONE small goal",
                "Avoid irreversible decisions",
                "Re-evaluate in 2 weeks"
            ]
        )

    if risk >= 4:
        return (
            "High Risk – Avoid",
            "This situation has financial or urgency risk.",
            [
                "Do NOT spend money now",
                "Verify with trusted sources",
                "Delay decision by 7 days"
            ]
        )

    return (
        "Safe to Proceed Slowly",
        "No immediate danger detected. Move step by step.",
        [
            "Research from official sources",
            "Take small actions only",
            "Track progress weekly"
        ]
    )

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/decide", methods=["POST"])
def decide():
    stage = request.form["stage"]
    problem = request.form["problem"]

    status, reason, steps = decision_engine(stage, problem)

    if "user_id" in session:
        conn = get_db()
        conn.execute(
            "INSERT INTO decisions (user_id, stage, problem, result) VALUES (?, ?, ?, ?)",
            (session["user_id"], stage, problem, status)
        )
        conn.commit()
        conn.close()

    return render_template(
        "result.html",
        status=status,
        reason=reason,
        steps=steps
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
