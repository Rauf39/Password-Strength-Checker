from flask import Flask, render_template, request, jsonify
import re
import random
import string

app = Flask(__name__)

# Функция проверки пароля
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

    # Заглавные буквы
    if re.search(r"[A-Z]", password):
        score += 15
    else:
        recommendations.append("Add uppercase letters")

    # Спецсимволы
    if re.search(r"[@$!%*?&]", password):
        score += 20
    else:
        recommendations.append("Add special characters (@, $, !, %, etc.)")

    # Маленькие буквы
    if re.search(r"[a-z]", password):
        score += 25
    else:
        recommendations.append("Add lowercase letters")

    if score > 100:
        score = 100

    return score, recommendations

# Генератор пароля
def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "@$!%*?&"
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    password = data.get("password", "")
    score, recs = check_password_strength(password)
    return jsonify({"score": score, "recommendations": recs})

@app.route('/generate', methods=['GET'])
def generate():
    pwd = generate_password()
    return jsonify({"password": pwd})

if __name__ == "__main__":
    app.run(debug=True)
