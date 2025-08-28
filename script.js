document.addEventListener("DOMContentLoaded", () => {
  const pwInput = document.getElementById("password");
  const checkBtn = document.getElementById("check");
  const genBtn = document.getElementById("generate");
  const last5Btn = document.getElementById("last5");
  const clearBtn = document.getElementById("clear");
  const toggleBtn = document.getElementById("toggle");
  const copyBtn = document.getElementById("copy");
  const themeBtn = document.getElementById("theme-btn");

  const progressBar = document.getElementById("progress-bar");
  const recsList = document.getElementById("recs");
  const timeTxt = document.getElementById("time");
  const breachTxt = document.getElementById("breach");
  const historyBox = document.getElementById("history-box");
  const historyList = document.getElementById("history");

  // toggle
  toggleBtn.addEventListener("click", () => {
    pwInput.type = pwInput.type === "password" ? "text" : "password";
  });

  // copy
  copyBtn.addEventListener("click", () => {
    if (!pwInput.value) return;
    navigator.clipboard.writeText(pwInput.value);
    copyBtn.innerText = "✔";
    setTimeout(() => (copyBtn.innerText = "Copy"), 1200);
  });

  // check
  checkBtn.addEventListener("click", async () => {
    if (!pwInput.value) return;
    const res = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pwInput.value }),
    });
    const data = await res.json();

    progressBar.style.width = data.score + "%";
    progressBar.innerText = data.score + "%";

    recsList.innerHTML = "";
    data.recommendations.forEach(r => {
      let li = document.createElement("li");
      li.innerText = r;
      li.style.animation = "fadeIn 0.5s";
      recsList.appendChild(li);
    });

    timeTxt.innerText = document.body.classList.contains("dark")
      ? "🌙 " + data.time
      : "⏳ " + data.time;
    breachTxt.innerText = data.compromised ? "⚠️ Pwned!" : "✅ Safe";

    historyList.innerHTML = "";
    data.history.forEach(p => {
      let li = document.createElement("li");
      li.innerText = p;
      historyList.appendChild(li);
    });
  });

  // generate always strong
  genBtn.addEventListener("click", async () => {
    const res = await fetch("/generate");
    const data = await res.json();
    pwInput.value = data.password;

    // auto-check after generation
    checkBtn.click();
  });

  // last5 toggle
  last5Btn.addEventListener("click", () => {
    historyBox.classList.toggle("hidden");
  });

  // clear
  clearBtn.addEventListener("click", async () => {
    await fetch("/clear", { method: "POST" });
    historyList.innerHTML = "";
  });

  // theme
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    themeBtn.innerText = document.body.classList.contains("dark") ? "☀️" : "🌙";
  });
});
