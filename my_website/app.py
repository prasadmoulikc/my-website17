from flask import request, redirect
from flask import Flask,render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    return conn

@app.route("/")
def home():
    conn =get_db_connection()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()
    return render_template("index.html",posts=posts)

@app.route("/create",
methods=["posts"])
def create():
    title = request.form["title"]
    content = request.form["content"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        (title, content)
    )
    conn.commit()
    conn.close() 
    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()