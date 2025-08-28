from flask import Flask, render_template, request, jsonify, session
import requests
import hashlib
import random
import string
import math

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Переводы
translations = {
    "en": {
        "title": "Password Strength Checker",
        "enter_password": "Enter your password:",
        "check": "Check",
        "generate": "Generate",
        "last5": "Last 5",
        "clear": "Clear",
        "copy": "Copy",
        "toggle": "Show/Hide",
        "recommendations": "Recommendations",
        "history": "Password History",
        "compromised": "⚠️ This password was found in a data breach!",
        "not_compromised": "✅ This password has not been found in breaches.",
        "entropy": "Entropy bits: ",
        "batch": "Batch Check"
    },
    "ru": {
        "title": "Проверка надежности пароля",
        "enter_password": "Введите пароль:",
        "check": "Проверить",
        "generate": "Сгенерировать",
        "last5": "Последние 5",
        "clear": "Очистить",
        "copy": "Скопировать",
        "toggle": "Показать/Скрыть",
        "recommendations": "Рекомендации",
        "history": "История паролей",
        "compromised": "⚠️ Этот пароль найден в утечках!",
        "not_compromised": "✅ Этот пароль не найден в утечках.",
        "entropy": "Энтропия (бит): ",
        "batch": "Массовая проверка"
    },
    "az": {
        "title": "Şifrə Güclülük Yoxlayıcı",
        "enter_password": "Şifrənizi daxil edin:",
        "check": "Yoxla",
        "generate": "Yarat",
        "last5": "Son 5",
        "clear": "Təmizlə",
        "copy": "Kopyala",
        "toggle": "Göstər/Gizlə",
        "recommendations": "Tövsiyələr",
        "history": "Şifrə Tarixi",
        "compromised": "⚠️ Bu şifrə sızıntılarda tapılıb!",
        "not_compromised": "✅ Bu şifrə sızıntılarda tapılmayıb.",
        "entropy": "Entropiya bitləri: ",
        "batch": "Kütləvi yoxlama"
    }
}

def password_strength(password: str) -> dict:
    score = 0
    recs = []

    if len(password) >= 8: score += 20
    else: recs.append("Use at least 8 characters.")

    if any(c.islower() for c in password): score += 20
    else: recs.append("Add lowercase letters.")

    if any(c.isupper() for c in password): score += 20
    else: recs.append("Add uppercase letters.")

    if any(c.isdigit() for c in password): score += 20
    else: recs.append("Add numbers.")

    if any(c in string.punctuation for c in password): score += 20
    else: recs.append("Add special characters.")

    # Gamification
    message = "⚠ Weak! Too risky!"
    if score >= 60:
        message = "💡 Medium, can be improved."
    if score >= 80:
        message = "🔥 Excellent! Hacker-proof!"

    return {"score": min(score, 100), "recommendations": recs, "message": message}

def time_to_crack(password: str) -> dict:
    length = len(password)
    if length < 6:
        return {"pc": "instantly", "gpu": "instantly", "super": "instantly"}
    elif length < 8:
        return {"pc": "minutes", "gpu": "seconds", "super": "milliseconds"}
    elif length < 10:
        return {"pc": "hours", "gpu": "minutes", "super": "seconds"}
    elif length < 12:
        return {"pc": "days", "gpu": "hours", "super": "minutes"}
    elif length < 16:
        return {"pc": "years", "gpu": "months", "super": "days"}
    else:
        return {"pc": "centuries", "gpu": "years", "super": "months"}

def entropy(password: str) -> int:
    charset = 0
    if any(c.islower() for c in password): charset += 26
    if any(c.isupper() for c in password): charset += 26
    if any(c.isdigit() for c in password): charset += 10
    if any(c in string.punctuation for c in password): charset += len(string.punctuation)
    if charset == 0: return 0
    return round(len(password) * math.log2(charset))

def check_pwned(password: str) -> bool:
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)
    if res.status_code == 200:
        for line in res.text.splitlines():
            h, _ = line.split(":")
            if h == suffix:
                return True
    return False

@app.route("/")
def index():
    lang = request.args.get("lang") or session.get("lang", "en")
    if lang not in translations:
        lang = "en"
    session["lang"] = lang
    return render_template("index.html", t=translations[lang], lang=lang)

@app.route("/check", methods=["POST"])
def check():
    pw = request.json.get("password", "")
    save = request.json.get("save", False)  # флаг: сохранять ли в историю
    result = password_strength(pw)
    cracked = time_to_crack(pw)
    comp = check_pwned(pw)
    ent = entropy(pw)

    if "history" not in session:
        session["history"] = []

    # Сохраняем только если нажата кнопка Check
    if save and pw and pw not in session["history"]:
        session["history"].insert(0, pw)
        session["history"] = session["history"][:5]

    session.modified = True
    return jsonify({
        "score": result["score"],
        "recommendations": result["recommendations"],
        "message": result["message"],
        "time": cracked,
        "compromised": comp,
        "entropy": ent,
        "history": session["history"]
    })

@app.route("/generate")
def generate():
    chars = string.ascii_letters + string.digits + string.punctuation
    pw = "".join(random.choice(chars) for _ in range(18))
    return jsonify({"password": pw})

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "cleared"})

@app.route("/batch", methods=["POST"])
def batch():
    file = request.files["file"]
    content = file.read().decode("utf-8").splitlines()
    results = []
    for pw in content:
        res = password_strength(pw)
        results.append({
            "password": pw,
            "score": res["score"],
            "message": res["message"],
            "compromised": check_pwned(pw),
            "entropy": entropy(pw)
        })
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="192.168.0.107", port=5002, debug=True)
