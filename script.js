document.getElementById("check").addEventListener("click", async () => {
    const password = document.getElementById("password").value;

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
        bar.style.background = "green";
    }

    const recs = document.getElementById("recommendations");
    recs.innerHTML = "";
    data.recommendations.forEach(r => {
        let li = document.createElement("li");
        li.textContent = r;
        recs.appendChild(li);
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
    alert("Password copied!");
});

document.getElementById("toggle").addEventListener("click", () => {
    const pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
});
