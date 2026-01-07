import sqlite3
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_FILE = "ml_model.pkl"

def train_model():
    if not os.path.exists("database.db"):
        return

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT question, rating
        FROM feedback
        WHERE rating IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    if len(rows) < 5:
        return  # not enough data yet

    X = [r[0] for r in rows]
    y = [1 if r[1] >= 3 else 0 for r in rows]

    vectorizer = TfidfVectorizer()
    X_vec = vectorizer.fit_transform(X)

    model = LogisticRegression()
    model.fit(X_vec, y)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump((vectorizer, model), f)


def predict_quality(question):
    if not os.path.exists(MODEL_FILE):
        return "medium"

    with open(MODEL_FILE, "rb") as f:
        vectorizer, model = pickle.load(f)

    X = vectorizer.transform([question])
    pred = model.predict(X)[0]

    return "high" if pred == 1 else "low"
