const API_BASE = "http://localhost:8000";
const EXPLAIN_ENDPOINT = `${API_BASE}/explain`;
const GENERATE_ENDPOINT = `${API_BASE}/generate`;

// DOM refs
const passwordInput      = document.getElementById("passwordInput");
const analyzeBtn         = document.getElementById("analyzeBtn");
const generateBtn        = document.getElementById("generateBtn");
const toggleBtn          = document.getElementById("toggleVisibility");
const themeToggle        = document.getElementById("themeToggle");
const resultSection      = document.getElementById("resultSection");
const securityLevel      = document.getElementById("securityLevel");
const riskScore          = document.getElementById("riskScore");
const progressBar        = document.getElementById("progressBar");
const scoreMessage       = document.getElementById("scoreMessage");
const reasonsSection     = document.getElementById("reasonsSection");
const reasonsList        = document.getElementById("reasonsList");
const suggestionsSection = document.getElementById("suggestionsSection");
const suggestionsList    = document.getElementById("suggestionsList");
const generatedSection   = document.getElementById("generatedSection");
const generatedPassword  = document.getElementById("generatedPassword");
const copyBtn            = document.getElementById("copyBtn");
const alternativesSection = document.getElementById("alternativesSection");
const alternativesList   = document.getElementById("alternativesList");
const dashboardSection   = document.getElementById("dashboardSection");
const toastContainer     = document.getElementById("toastContainer");

// Dashboard elements
const valLength   = document.getElementById("val-length");
const valUpper    = document.getElementById("val-upper");
const valLower    = document.getElementById("val-lower");
const valDigit    = document.getElementById("val-digit");
const valSpecial  = document.getElementById("val-special");
const valPatterns = document.getElementById("val-patterns");
const dashCards = {
  upper: document.getElementById("dash-upper"),
  lower: document.getElementById("dash-lower"),
  digit: document.getElementById("dash-digit"),
  special: document.getElementById("dash-special"),
  patterns: document.getElementById("dash-patterns"),
};

const LEVEL_MAP = {
  "Çok Zayıf": { cls: "very-weak",   bar: 8  },
  "Zayıf":     { cls: "weak",         bar: 25 },
  "Orta":      { cls: "medium",       bar: 50 },
  "Güçlü":     { cls: "strong",       bar: 75 },
  "Çok Güçlü": { cls: "very-strong",  bar: 95 },
};

const SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?";

// ===== Toast =====
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ===== Theme =====
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeToggle.textContent = theme === "dark" ? "🌙" : "☀️";
  localStorage.setItem("theme", theme);
}

themeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
});

// Restore theme
applyTheme(localStorage.getItem("theme") || "dark");

// ===== Dashboard: real-time criteria check =====
function updateDashboard(pw) {
  if (!pw) {
    dashboardSection.classList.add("hidden");
    return;
  }
  dashboardSection.classList.remove("hidden");

  const hasUpper   = /[A-Z]/.test(pw);
  const hasLower   = /[a-z]/.test(pw);
  const hasDigit   = /[0-9]/.test(pw);
  const hasSpecial = pw.split("").some(c => SPECIAL_CHARS.includes(c));

  valLength.textContent = pw.length;
  valUpper.textContent   = hasUpper   ? "✔" : "✗";
  valLower.textContent   = hasLower   ? "✔" : "✗";
  valDigit.textContent   = hasDigit   ? "✔" : "✗";
  valSpecial.textContent = hasSpecial ? "✔" : "✗";

  dashCards.upper.className   = `dash-card ${hasUpper   ? "ok" : "fail"}`;
  dashCards.lower.className   = `dash-card ${hasLower   ? "ok" : "fail"}`;
  dashCards.digit.className   = `dash-card ${hasDigit   ? "ok" : "fail"}`;
  dashCards.special.className = `dash-card ${hasSpecial ? "ok" : "fail"}`;
}

// ===== Normalizers =====
const normalizeScore   = d => Number(d.security_score ?? d.final_score ?? d.risk_score ?? d.score ?? 0);
const normalizeLevel   = d => d.security_level ?? d.level ?? d.strength ?? "Orta";
const normalizeMessage = d => d.assessment ?? d.message ?? d.explanation ?? "";
const normalizeSuggestions = d => d.suggestions ?? d.recommendations ?? d.feedback ?? [];
const normalizeReasons = d => {
  const out = [];
  (d.missing_requirements ?? []).forEach(r => out.push(`Eksik: ${r}`));
  (d.pattern_warnings     ?? []).forEach(r => out.push(`Risk deseni: ${r}`));
  (d.patterns             ?? []).forEach(r => out.push(`Tespit edilen desen: ${r}`));
  (d.feedback             ?? []).forEach(r => { if (!out.includes(r)) out.push(r); });
  return out;
};

// ===== Render list =====
function renderList(section, list, items) {
  list.innerHTML = "";
  if (!items?.length) { section.classList.add("hidden"); return; }
  items.forEach((item, i) => {
    const li = document.createElement("li");
    li.textContent = item;
    li.style.animationDelay = `${i * 0.05}s`;
    list.appendChild(li);
  });
  section.classList.remove("hidden");
}

// ===== Render score =====
function renderScore(data) {
  const levelKey = normalizeLevel(data);
  const score    = normalizeScore(data);
  const info     = LEVEL_MAP[levelKey] ?? { cls: "medium", bar: 50 };

  securityLevel.textContent = levelKey;
  securityLevel.className   = `security-level level-${info.cls}`;
  riskScore.textContent     = `${score} / 100`;

  // Güvenlik seviyesine göre bar genişliği (zayıf → geniş çubuk)
  const barWidth = info.bar;
  progressBar.style.width    = `${barWidth}%`;
  progressBar.className      = `progress-bar bar-${info.cls}`;
  scoreMessage.textContent   = normalizeMessage(data);

  renderList(reasonsSection,     reasonsList,     normalizeReasons(data));
  renderList(suggestionsSection, suggestionsList, normalizeSuggestions(data));

  resultSection.classList.remove("hidden");

  // Dashboard pattern count update from API
  const patternCount = (data.pattern_warnings ?? data.patterns ?? []).length;
  valPatterns.textContent = patternCount;
  dashCards.patterns.className = `dash-card ${patternCount > 0 ? "fail" : "ok"}`;
}

// ===== API helper =====
async function postJson(url, payload = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  let data = {};
  try { data = await res.json(); } catch { /**/ }
  if (!res.ok) throw new Error(data.detail ?? data.message ?? "Bir hata oluştu.");
  return data;
}

// ===== Analyze =====
let analyzeDebounce = null;

async function analyzePassword(silent = false) {
  const pw = passwordInput.value;
  if (!pw.trim()) {
    if (!silent) showToast("Lütfen bir parola girin.", "error");
    return;
  }
  updateDashboard(pw);
  resultSection.classList.add("hidden");

  try {
    const data = await postJson(EXPLAIN_ENDPOINT, { password: pw });
    renderScore(data);
    if (!silent) showToast("Analiz tamamlandı.", "success");
  } catch (err) {
    if (!silent) showToast(err.message ?? "API'ye bağlanılamadı.", "error");
  }
}

// ===== Generate =====
function renderAlt(alt) {
  const item = document.createElement("div");
  item.className = "alt-item";
  const code = document.createElement("code");
  code.textContent = alt.password ?? alt;
  const btn = document.createElement("button");
  btn.className = "btn btn-copy";
  btn.textContent = "📋";
  btn.title = "Kopyala";
  btn.addEventListener("click", () => {
    navigator.clipboard.writeText(code.textContent).then(() => showToast("Kopyalandı!", "success"));
  });
  item.appendChild(code);
  item.appendChild(btn);
  return item;
}

async function generateSecurePassword() {
  generatedSection.classList.add("hidden");

  try {
    const data = await postJson(GENERATE_ENDPOINT, {
      length: 16, count: 3,
      use_uppercase: true, use_lowercase: true,
      use_digits: true, use_special: true,
    });

    const pw = data.generated_password ?? data.password ?? data.secure_password ?? "";
    generatedPassword.textContent = pw;
    generatedSection.classList.remove("hidden");
    showToast("Güvenli parola üretildi!", "success");

    if (pw) {
      passwordInput.value = pw;
      updateDashboard(pw);
      renderScore(data);
    }

    // Alternatifler
    const alts = data.alternatives ?? [];
    alternativesList.innerHTML = "";
    if (alts.length > 0) {
      alts.forEach(alt => alternativesList.appendChild(renderAlt(alt)));
      alternativesSection.classList.remove("hidden");
    } else {
      alternativesSection.classList.add("hidden");
    }
  } catch (err) {
    showToast(err.message ?? "API'ye bağlanılamadı.", "error");
  }
}

// ===== Copy =====
copyBtn.addEventListener("click", () => {
  const pw = generatedPassword.textContent;
  if (!pw) return;
  navigator.clipboard.writeText(pw).then(() => {
    copyBtn.textContent = "✅ Kopyalandı!";
    showToast("Parola panoya kopyalandı.", "success");
    setTimeout(() => { copyBtn.textContent = "📋 Kopyala"; }, 2000);
  });
});

// ===== Events =====
analyzeBtn.addEventListener("click", () => analyzePassword(false));
generateBtn.addEventListener("click", generateSecurePassword);

toggleBtn.addEventListener("click", () => {
  const hidden = passwordInput.type === "password";
  passwordInput.type = hidden ? "text" : "password";
  toggleBtn.textContent = hidden ? "🙈" : "👁";
});

passwordInput.addEventListener("keydown", e => { if (e.key === "Enter") analyzePassword(false); });

// Real-time dashboard update + debounced analysis
passwordInput.addEventListener("input", () => {
  updateDashboard(passwordInput.value);
  clearTimeout(analyzeDebounce);
  if (passwordInput.value.trim().length >= 4) {
    analyzeDebounce = setTimeout(() => analyzePassword(true), 600);
  }
});
