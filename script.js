document.addEventListener("DOMContentLoaded", () => {
  const pwInput = document.getElementById("password");
  const checkBtn = document.getElementById("check");
  const genBtn = document.getElementById("generate");
  const last5Btn = document.getElementById("last5");
  const clearBtn = document.getElementById("clear");
  const toggleBtn = document.getElementById("toggle");
  const copyBtn = document.getElementById("copy");
  const themeBtn = document.getElementById("theme-btn");
  const batchBtn = document.getElementById("batch-btn");
  const batchFile = document.getElementById("batch-file");
  const batchClear = document.getElementById("batch-clear");
  const batchResults = document.getElementById("batch-results");

  const progressBar = document.getElementById("progress-bar");
  const recsList = document.getElementById("recs");
  const msgTxt = document.getElementById("message");
  const timeTxt = document.getElementById("time");
  const entTxt = document.getElementById("entropy");
  const breachTxt = document.getElementById("breach");
  const historyBox = document.getElementById("history-box");
  const historyList = document.getElementById("history");

  // === ЯЗЫКИ ===
  window.setLang = function(lang) {
    window.location.href = "/?lang=" + lang;
  };

  // === Copy password ===
  copyBtn.addEventListener("click", () => {
    if (!pwInput.value) return;
    const temp = document.createElement("textarea");
    temp.value = pwInput.value;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand("copy");
    document.body.removeChild(temp);
    copyBtn.innerText = "Copied!";
    setTimeout(() => (copyBtn.innerText = "Copy"), 1500);
  });

  // === Toggle password ===
  toggleBtn.addEventListener("click", () => {
    pwInput.type = pwInput.type === "password" ? "text" : "password";
  });

  // === Check password ===
  async function checkPassword(saveToHistory = false) {
    if (!pwInput.value) return;
    const res = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pwInput.value, save: saveToHistory }),
    });
    const data = await res.json();

    progressBar.style.width = data.score + "%";
    progressBar.innerText = data.score + "%";

    msgTxt.innerText = data.message;

    recsList.innerHTML = "";
    data.recommendations.forEach(r => {
      let li = document.createElement("li");
      li.innerText = r;
      recsList.appendChild(li);
    });

    timeTxt.innerHTML = `💻 PC: ${data.time.pc} | 🎮 GPU: ${data.time.gpu} | ⚡ Super: ${data.time.super}`;
    entTxt.innerText = "🔑 Entropy: " + data.entropy + " bits";
    breachTxt.innerText = data.compromised ? "⚠️ Pwned!" : "✅ Safe";

    if (saveToHistory) {
      historyList.innerHTML = "";
      data.history.forEach(p => {
        let li = document.createElement("li");
        li.innerText = p;
        historyList.appendChild(li);
      });
    }
  }

  // Нажатие Check → сохраняем в history
  checkBtn.addEventListener("click", () => checkPassword(true));

  // При вводе → обновляем, но без записи в history
  pwInput.addEventListener("input", () => checkPassword(false));

  // === Generate password ===
  genBtn.addEventListener("click", async () => {
    const res = await fetch("/generate");
    const data = await res.json();
    pwInput.value = data.password;
    checkPassword(false); // только показать, не сохранять
  });

  // === Last 5 toggle ===
  last5Btn.addEventListener("click", () => {
    historyBox.classList.toggle("hidden");
  });

  // === Clear history ===
  clearBtn.addEventListener("click", async () => {
    await fetch("/clear", { method: "POST" });
    historyList.innerHTML = "";
  });

  // === Theme toggle ===
  let themes = ["light", "dark", "matrix", "blue"];
  let current = localStorage.getItem("theme") || "light";
  if (current !== "light") document.body.classList.add(current);

  function updateThemeIcon() {
    if (current === "dark") themeBtn.innerText = "☀️";
    else if (current === "matrix") themeBtn.innerText = "🟢";
    else if (current === "blue") themeBtn.innerText = "🌊";
    else themeBtn.innerText = "🌙";
  }
  updateThemeIcon();

  themeBtn.addEventListener("click", () => {
    document.body.classList.remove(current);
    let idx = (themes.indexOf(current) + 1) % themes.length;
    current = themes[idx];
    if (current !== "light") document.body.classList.add(current);
    localStorage.setItem("theme", current);
    updateThemeIcon();
  });

  // === Batch check ===
  batchBtn.addEventListener("click", async () => {
    if (!batchFile.files.length) {
      alert("Please upload a TXT file with passwords.");
      return;
    }
    const formData = new FormData();
    formData.append("file", batchFile.files[0]);

    const res = await fetch("/batch", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    batchResults.innerHTML = "";
    data.forEach(item => {
      let li = document.createElement("li");
      li.innerHTML = `${item.password} → ${item.score}% | ${item.message} | 🔑 ${item.entropy} bits | ${item.compromised ? "⚠️ Pwned!" : "✅ Safe"}`;
      batchResults.appendChild(li);
    });
  });

  // === Clear batch results ===
  batchClear.addEventListener("click", () => {
    batchResults.innerHTML = "";
    batchFile.value = "";
  });
});
