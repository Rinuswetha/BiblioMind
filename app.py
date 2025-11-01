from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import datetime
import os

app = Flask(__name__)
app.secret_key = "replace_this_with_a_real_secret_in_production"

RESULTS_FILE = "results.json"

# curated book picks by genre
BOOKS = {
    "Romance": ["The Rosie Project", "Eleanor & Park", "Me Before You", "Pride and Prejudice"],
    "Thriller": ["Gone Girl", "The Girl on the Train", "The Silent Patient", "The Da Vinci Code"],
    "Fantasy": ["Harry Potter and the Sorcerer's Stone", "The Hobbit", "The Name of the Wind", "Percy Jackson & the Lightning Thief"],
    "Self-Help": ["Atomic Habits", "The 7 Habits of Highly Effective People", "Mindset", "You Are a Badass"]
}

# mapping per question option -> genre (A,B,C,D)
MAPPINGS = [
    {"A": "Romance", "B": "Thriller", "C": "Fantasy", "D": "Self-Help"},  # q1
    {"A": "Romance", "B": "Thriller", "C": "Fantasy", "D": "Self-Help"},  # q2
    {"A": "Romance", "B": "Thriller", "C": "Fantasy", "D": "Self-Help"},  # q3
    {"A": "Romance", "B": "Thriller", "C": "Fantasy", "D": "Self-Help"},  # q4
    {"A": "Romance", "B": "Thriller", "C": "Fantasy", "D": "Self-Help"}   # q5
]

def save_result(name, answers, genre):
    record = {
        "name": name,
        "answers": answers,
        "genre": genre,
        "time": datetime.datetime.now().isoformat()
    }
    try:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []
    data.append(record)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def compute_genre(answers):
    scores = {}
    for i, choice in enumerate(answers):
        mapping = MAPPINGS[i]
        genre = mapping.get(choice)
        if genre:
            scores[genre] = scores.get(genre, 0) + 1
    if not scores:
        return "Motivational"  # fallback
    # pick max score; tie-breaker: Romance > Fantasy > Thriller > Self-Help (stable)
    ordered = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return ordered[0][0]

@app.route("/")
def welcome():
    # clear previous session answers when landing on welcome
    session.pop("answers", None)
    session.pop("name", None)
    return render_template("welcome.html")

@app.route("/q1", methods=["GET","POST"])
def q1():
    if request.method == "POST":
        name = request.form.get("name","Reader").strip() or "Reader"
        session["name"] = name
        session["answers"] = []
        choice = request.form.get("choice")
        if choice:
            session["answers"].append(choice)
        return redirect(url_for("q2"))
    return render_template("q1.html")

@app.route("/q2", methods=["GET","POST"])
def q2():
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice:
            session["answers"].append(choice)
        return redirect(url_for("q3"))
    return render_template("q2.html")

@app.route("/q3", methods=["GET","POST"])
def q3():
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice:
            session["answers"].append(choice)
        return redirect(url_for("q4"))
    return render_template("q3.html")

@app.route("/q4", methods=["GET","POST"])
def q4():
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice:
            session["answers"].append(choice)
        return redirect(url_for("q5"))
    return render_template("q4.html")

@app.route("/q5", methods=["GET","POST"])
def q5():
    # 5th testing question
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice:
            session["answers"].append(choice)
        # after q5, go to loading
        return redirect(url_for("loading"))
    return render_template("q5.html")

@app.route("/loading")
def loading():
    # loading animation, then redirect to result after short wait via JS
    return render_template("loading.html")

@app.route("/result")
def result():
    answers = session.get("answers", [])
    name = session.get("name", "Reader")
    genre = compute_genre(answers)
    curated = BOOKS.get(genre, [])
    # optional: save
    try:
        save_result(name, answers, genre)
    except Exception:
        pass
    return render_template("result.html", name=name, genre=genre, curated=curated, answers=answers)

if __name__ == "__main__":
    app.run(debug=True)
