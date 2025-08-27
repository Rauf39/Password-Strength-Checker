from flask import Flask, render_template, request, jsonify, session
import re
import random
import string
import requests

app = Flask(__name__)
app.secret_key = "supersecret"  # для хранения истории в сессии

# --- Проверка пароля ---
def check_password_strength(password):
    score = 0
    recommendations = []

    # Длина
    if len(password) >= 12:
        score += 25
    else:
        recommendations.append("Use at least 12 characters")

    # Цифры
    if re.search(r"\d", password):
        score += 15
    else:
        recommendations.append("Add numbers")

    # Заглавные
    if re.search(r"[A-Z]", password):
        score += 15
    else:
        recommendations.append("Add uppercase letters")

    # Спецсимволы
    if re.search(r"[@$!%*?&]", password):
        score += 20
    else:
        recommendations.append("Add special characters (@, $, !, %, etc.)")

    # Строчные
    if re.search(r"[a-z]", password):
        score += 25
    else:
        recommendations.append("Add lowercase letters")

    score = min(score, 100)

    # Примерная оценка времени взлома
    crack_time = estimate_crack_time(len(password), score)

    return score, recommendations, crack_time


def estimate_crack_time(length, score):
    if length < 6:
        return "Instantly"
    elif score < 40:
        return "Few seconds"
    elif score < 70:
        return "Minutes to hours"
    elif score < 90:
        return "Days to months"
    else:
        return "Centuries"


# --- Генератор пароля ---
def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "@$!%*?&"
    return ''.join(random.choice(chars) for _ in range(length))


# --- Проверка утечек ---
def check_pwned(password):
    sha1 = __import__('hashlib').sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)
    if res.status_code != 200:
        return False, 0
    hashes = (line.split(':') for line in res.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return True, int(count)
    return False, 0


@app.route('/')
def index():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html")


@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    password = data.get("password", "")

    score, recs, crack_time = check_password_strength(password)
    breached, count = check_pwned(password)

    # история (уникальные, последние 5)
    history = session.get("history", [])
    if password and password not in history:
        history.insert(0, password)
        history = history[:5]
    session["history"] = history

    return jsonify({
        "score": score,
        "recommendations": recs,
        "crack_time": crack_time,
        "breached": breached,
        "count": count,
        "history": history
    })


@app.route('/generate', methods=['GET'])
def generate():
    pwd = generate_password()
    return jsonify({"password": pwd})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
