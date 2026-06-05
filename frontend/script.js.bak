const API_BASE = "http://localhost:8000";

const passwordInput = document.getElementById("passwordInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const generateBtn = document.getElementById("generateBtn");
const toggleBtn = document.getElementById("toggleVisibility");
const resultSection = document.getElementById("resultSection");
const securityLevel = document.getElementById("securityLevel");
const riskScore = document.getElementById("riskScore");
const progressBar = document.getElementById("progressBar");
const scoreMessage = document.getElementById("scoreMessage");
const patternsSection = document.getElementById("patternsSection");
const patternsList = document.getElementById("patternsList");
const generatedSection = document.getElementById("generatedSection");
const generatedPassword = document.getElementById("generatedPassword");
const copyBtn = document.getElementById("copyBtn");
const errorMsg = document.getElementById("errorMsg");

const LEVEL_MAP = {
  "Çok Zayıf":  { cls: "very-weak",   bar: 95 },
  "Zayıf":      { cls: "weak",         bar: 75 },
  "Orta":       { cls: "medium",       bar: 50 },
  "Güçlü":      { cls: "strong",       bar: 25 },
  "Çok Güçlü":  { cls: "very-strong",  bar: 8  },
};

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove("hidden");
}

function clearError() {
  errorMsg.classList.add("hidden");
  errorMsg.textContent = "";
}

function renderScore(data) {
  clearError();
  const levelKey = data.security_level;
  const info = LEVEL_MAP[levelKey] || { cls: "medium", bar: 50 };

  securityLevel.textContent = levelKey;
  securityLevel.className = `security-level level-${info.cls}`;
  riskScore.textContent = `${data.risk_score}`;
  progressBar.style.width = `${info.bar}%`;
  progressBar.className = `progress-bar bar-${info.cls}`;
  scoreMessage.textContent = data.message;

  patternsList.innerHTML = "";
  if (data.weak_patterns && data.weak_patterns.length > 0) {
    data.weak_patterns.forEach((p) => {
      const li = document.createElement("li");
      li.textContent = p;
      patternsList.appendChild(li);
    });
    patternsSection.classList.remove("hidden");
  } else {
    patternsSection.classList.add("hidden");
  }

  resultSection.classList.remove("hidden");
}

analyzeBtn.addEventListener("click", async () => {
  const pw = passwordInput.value;
  if (!pw.trim()) {
    showError("Lütfen bir parola girin.");
    return;
  }
  clearError();
  resultSection.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pw }),
    });
    if (!res.ok) {
      const err = await res.json();
      showError(err.detail || "Bir hata oluştu.");
      return;
    }
    const data = await res.json();
    renderScore(data);
  } catch {
    showError("API'ye bağlanılamadı. Backend çalışıyor mu?");
  }
});

generateBtn.addEventListener("click", async () => {
  clearError();
  generatedSection.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/generate`, { method: "POST" });
    if (!res.ok) {
      showError("Parola üretilirken hata oluştu.");
      return;
    }
    const data = await res.json();
    generatedPassword.textContent = data.password;
    generatedSection.classList.remove("hidden");
  } catch {
    showError("API'ye bağlanılamadı. Backend çalışıyor mu?");
  }
});

copyBtn.addEventListener("click", () => {
  const pw = generatedPassword.textContent;
  if (pw) {
    navigator.clipboard.writeText(pw).then(() => {
      copyBtn.textContent = "Kopyalandı!";
      setTimeout(() => { copyBtn.textContent = "Kopyala"; }, 2000);
    });
  }
});

toggleBtn.addEventListener("click", () => {
  const isHidden = passwordInput.type === "password";
  passwordInput.type = isHidden ? "text" : "password";
  toggleBtn.textContent = isHidden ? "🙈" : "👁";
});

passwordInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") analyzeBtn.click();
});
