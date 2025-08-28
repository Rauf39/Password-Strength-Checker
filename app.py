from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import hashlib
import random
import string

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
        "time": "⏳ Time to crack: "
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
        "time": "⏳ Время взлома: "
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
        "time": "⏳ Sındırılma vaxtı: "
    }
}

# Функции
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

    return {"score": min(score, 100), "recommendations": recs}

def time_to_crack(password: str) -> str:
    length = len(password)
    if length < 6: return "instantly"
    elif length < 8: return "minutes"
    elif length < 10: return "hours"
    elif length < 12: return "days"
    elif length < 16: return "years"
    else: return "centuries"

def check_pwned(password: str) -> bool:
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)
    if res.status_code == 200:
        for line in res.text.splitlines():
            h, count = line.split(":")
            if h == suffix:
                return True
    return False

# Роуты
@app.route("/")
def index():
    lang = session.get("lang", "en")
    return render_template("index.html", t=translations[lang], lang=lang)

@app.route("/setlang/<lang>")
def setlang(lang):
    if lang in translations:
        session["lang"] = lang
    return redirect(url_for("index"))

@app.route("/check", methods=["POST"])
def check():
    pw = request.json.get("password", "")
    result = password_strength(pw)
    cracked = time_to_crack(pw)
    compromised = check_pwned(pw)

    if "history" not in session:
        session["history"] = []
    if pw and pw not in session["history"]:
        session["history"].insert(0, pw)
        session["history"] = session["history"][:5]

    session.modified = True
    return jsonify({
        "score": result["score"],
        "recommendations": result["recommendations"],
        "time": cracked,
        "compromised": compromised,
        "history": session["history"]
    })

@app.route("/generate")
def generate():
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    pw = "".join(random.choice(chars) for _ in range(16))
    return jsonify({"password": pw})

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)
