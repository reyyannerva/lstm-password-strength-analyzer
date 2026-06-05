const API_BASE = "http://localhost:8000";

const SCORE_ENDPOINT = `${API_BASE}/score`;
const EXPLAIN_ENDPOINT = `${API_BASE}/explain`;
const GENERATE_ENDPOINT = `${API_BASE}/generate`;

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

const reasonsSection = document.getElementById("reasonsSection");
const reasonsList = document.getElementById("reasonsList");

const suggestionsSection = document.getElementById("suggestionsSection");
const suggestionsList = document.getElementById("suggestionsList");

const errorMsg = document.getElementById("errorMsg");

const LEVEL_MAP = {
  "Çok Zayıf": { cls: "very-weak", bar: 8 },
  "Zayıf": { cls: "weak", bar: 25 },
  "Orta": { cls: "medium", bar: 50 },
  "Güçlü": { cls: "strong", bar: 75 },
  "Çok Güçlü": { cls: "very-strong", bar: 95 },
};

function showError(message) {
  if (!errorMsg) return;

  errorMsg.textContent = message;
  errorMsg.classList.remove("hidden");
}

function clearError() {
  if (!errorMsg) return;

  errorMsg.textContent = "";
  errorMsg.classList.add("hidden");
}

function normalizeScore(data) {
  return Number(
    data.security_score ??
      data.final_score ??
      data.risk_score ??
      data.score ??
      0
  );
}

function normalizeLevel(data) {
  return (
    data.security_level ??
    data.level ??
    data.strength ??
    "Orta"
  );
}

function normalizeMessage(data) {
  return (
    data.assessment ??
    data.message ??
    data.explanation ??
    ""
  );
}

function normalizeSuggestions(data) {
  if (Array.isArray(data.suggestions)) return data.suggestions;
  if (Array.isArray(data.recommendations)) return data.recommendations;
  if (Array.isArray(data.feedback)) return data.feedback;

  return [];
}

function normalizeReasons(data) {
  const reasons = [];

  if (Array.isArray(data.missing_requirements)) {
    data.missing_requirements.forEach((item) => {
      reasons.push(`Eksik kural: ${item}`);
    });
  }

  if (Array.isArray(data.pattern_warnings)) {
    data.pattern_warnings.forEach((item) => {
      reasons.push(`Risk deseni: ${item}`);
    });
  }

  if (Array.isArray(data.patterns)) {
    data.patterns.forEach((item) => {
      reasons.push(`Tespit edilen desen: ${item}`);
    });
  }

  if (Array.isArray(data.feedback)) {
    data.feedback.forEach((item) => {
      if (!reasons.includes(item)) {
        reasons.push(item);
      }
    });
  }

  return reasons;
}

function renderList(section, list, items) {
  if (!section || !list) return;

  list.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    section.classList.add("hidden");
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });

  section.classList.remove("hidden");
}

function renderScore(data) {
  clearError();

  const levelKey = normalizeLevel(data);
  const score = normalizeScore(data);
  const message = normalizeMessage(data);
  const suggestions = normalizeSuggestions(data);
  const reasons = normalizeReasons(data);

  const info = LEVEL_MAP[levelKey] || {
    cls: "medium",
    bar: Math.max(0, Math.min(100, score)),
  };

  securityLevel.textContent = levelKey;
  securityLevel.className = `security-level level-${info.cls}`;

  riskScore.textContent = `${score} / 100`;

  progressBar.style.width = `${Math.max(0, Math.min(100, score || info.bar))}%`;
  progressBar.className = `progress-bar bar-${info.cls}`;

  scoreMessage.textContent = message;

  renderList(reasonsSection, reasonsList, reasons);
  renderList(suggestionsSection, suggestionsList, suggestions);

  if (patternsSection && patternsList) {
    const patternItems = Array.isArray(data.pattern_warnings)
      ? data.pattern_warnings
      : Array.isArray(data.patterns)
        ? data.patterns
        : [];

    renderList(patternsSection, patternsList, patternItems);
  }

  resultSection.classList.remove("hidden");
}

async function postJson(url, payload = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const detail = data.detail || data.message || "Bir hata oluştu.";
    throw new Error(detail);
  }

  return data;
}

async function analyzePassword() {
  const password = passwordInput.value;

  if (!password.trim()) {
    showError("Lütfen bir parola girin.");
    return;
  }

  clearError();
  resultSection.classList.add("hidden");

  try {
    const data = await postJson(EXPLAIN_ENDPOINT, { password });
    renderScore(data);
  } catch (error) {
    showError(error.message || "API'ye bağlanılamadı. Backend çalışıyor mu?");
  }
}

async function generateSecurePassword() {
  clearError();
  generatedSection.classList.add("hidden");

  try {
    const data = await postJson(GENERATE_ENDPOINT, {
      length: 16,
      use_uppercase: true,
      use_lowercase: true,
      use_digits: true,
      use_special: true,
    });

    const password =
      data.generated_password ||
      data.password ||
      data.secure_password ||
      "";

    generatedPassword.textContent = password;
    generatedSection.classList.remove("hidden");

    if (password) {
      passwordInput.value = password;
      renderScore(data);
    }
  } catch (error) {
    showError(error.message || "API'ye bağlanılamadı. Backend çalışıyor mu?");
  }
}

analyzeBtn.addEventListener("click", analyzePassword);
generateBtn.addEventListener("click", generateSecurePassword);

copyBtn.addEventListener("click", () => {
  const password = generatedPassword.textContent;

  if (!password) return;

  navigator.clipboard.writeText(password).then(() => {
    copyBtn.textContent = "Kopyalandı!";
    setTimeout(() => {
      copyBtn.textContent = "Kopyala";
    }, 2000);
  });
});

toggleBtn.addEventListener("click", () => {
  const isHidden = passwordInput.type === "password";

  passwordInput.type = isHidden ? "text" : "password";
  toggleBtn.textContent = isHidden ? "🙈" : "👁";
});

passwordInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    analyzePassword();
  }
});