document.getElementById("check").addEventListener("click", async () => {
    const password = document.getElementById("password").value;

    if (!password) {
        alert("Please enter a password!");
        return;
    }

    const res = await fetch("/check", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({password})
    });

    const data = await res.json();

    const bar = document.getElementById("progress-bar");
    bar.style.width = data.score + "%";
    bar.textContent = data.score + "%";

    if (data.score < 40) {
        bar.style.background = "red";
    } else if (data.score < 70) {
        bar.style.background = "orange";
    } else {
        bar.style.background = "linear-gradient(90deg, orange, green)";
    }

    document.getElementById("crack-time").textContent = "⏳ Estimated crack time: " + data.crack_time;

    if (data.breached) {
        document.getElementById("breach-info").textContent = `⚠️ Found in breaches (${data.count} times)`;
        document.getElementById("breach-info").style.color = "red";
    } else {
        document.getElementById("breach-info").textContent = "✅ Not found in breaches";
        document.getElementById("breach-info").style.color = "green";
    }

    const recs = document.getElementById("recommendations");
    recs.innerHTML = "";
    data.recommendations.forEach(r => {
        let li = document.createElement("li");
        li.textContent = "💡 " + r;
        recs.appendChild(li);
    });

    const hist = document.getElementById("history");
    hist.innerHTML = "";
    data.history.forEach(h => {
        let li = document.createElement("li");
        li.textContent = h;
        hist.appendChild(li);
    });
});

document.getElementById("generate").addEventListener("click", async () => {
    const res = await fetch("/generate");
    const data = await res.json();
    document.getElementById("password").value = data.password;
});

document.getElementById("copy").addEventListener("click", () => {
    const pwd = document.getElementById("password");
    pwd.select();
    document.execCommand("copy");

    let msg = document.createElement("div");
    msg.textContent = "Copied!";
    msg.style.position = "fixed";
    msg.style.bottom = "20px";
    msg.style.right = "20px";
    msg.style.background = "green";
    msg.style.color = "white";
    msg.style.padding = "10px";
    msg.style.borderRadius = "8px";
    document.body.appendChild(msg);

    setTimeout(() => msg.remove(), 1000);
});

document.getElementById("toggle").addEventListener("click", () => {
    const pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
});

document.getElementById("theme-toggle").addEventListener("click", () => {
    document.body.classList.toggle("dark");
});
