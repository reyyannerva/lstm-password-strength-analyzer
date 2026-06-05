const API_BASE = "http://localhost:8000";
const SCORE_ENDPOINT = `${API_BASE}/score`;
const EXPLAIN_ENDPOINT = `${API_BASE}/explain`;
const GENERATE_ENDPOINT = `${API_BASE}/generate`;

// DOM refs
const passwordInput = document.getElementById("passwordInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const generateBtn = document.getElementById("generateBtn");
const toggleBtn = document.getElementById("toggleVisibility");
const themeToggle = document.getElementById("themeToggle");

const resultSection = document.getElementById("resultSection");
const securityLevel = document.getElementById("securityLevel");
const riskScore = document.getElementById("riskScore");
const progressBar = document.getElementById("progressBar");
const scoreMessage = document.getElementById("scoreMessage");

const reasonsSection = document.getElementById("reasonsSection");
const reasonsList = document.getElementById("reasonsList");

const suggestionsSection = document.getElementById("suggestionsSection");
const suggestionsList = document.getElementById("suggestionsList");

const generatedSection = document.getElementById("generatedSection");
const generatedPassword = document.getElementById("generatedPassword");
const copyBtn = document.getElementById("copyBtn");

const alternativesSection = document.getElementById("alternativesSection");
const alternativesList = document.getElementById("alternativesList");

const dashboardSection = document.getElementById("dashboardSection");
const toastContainer = document.getElementById("toastContainer");

// Dashboard elements
const valLength = document.getElementById("val-length");
const valUpper = document.getElementById("val-upper");
const valLower = document.getElementById("val-lower");
const valDigit = document.getElementById("val-digit");
const valSpecial = document.getElementById("val-special");
const valPatterns = document.getElementById("val-patterns");

const dashCards = {
  upper: document.getElementById("dash-upper"),
  lower: document.getElementById("dash-lower"),
  digit: document.getElementById("dash-digit"),
  special: document.getElementById("dash-special"),
  patterns: document.getElementById("dash-patterns"),
};

const LEVEL_MAP = {
  "Çok Zayıf": { cls: "very-weak", bar: 8 },
  "Zayıf": { cls: "weak", bar: 25 },
  "Orta": { cls: "medium", bar: 50 },
  "Güçlü": { cls: "strong", bar: 75 },
  "Çok Güçlü": { cls: "very-strong", bar: 95 },
};

const SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?";

// ===== Utility =====
function safeText(value, fallback = "") {
  if (value === null || value === undefined) return fallback;
  return String(value);
}

function clearList(element) {
  if (!element) return;
  element.innerHTML = "";
}

function appendListItem(element, text) {
  if (!element) return;
  const li = document.createElement("li");
  li.textContent = safeText(text);
  element.appendChild(li);
}

function showElement(element) {
  if (element) element.classList.remove("hidden");
}

function hideElement(element) {
  if (element) element.classList.add("hidden");
}

function setButtonLoading(button, isLoading, loadingText, defaultText) {
  if (!button) return;

  button.disabled = isLoading;
  button.textContent = isLoading ? loadingText : defaultText;
}

// ===== Toast =====
function showToast(message, type = "info") {
  if (!toastContainer) {
    console.log(`[${type}] ${message}`);
    return;
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// ===== Theme =====
function applyTheme(theme) {
  if (!themeToggle) return;

  document.documentElement.setAttribute("data-theme", theme);
  themeToggle.textContent = theme === "dark" ? "🌙" : "☀️";
  localStorage.setItem("theme", theme);
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(current === "dark" ? "light" : "dark");
  });
}

applyTheme(localStorage.getItem("theme") || "dark");

// ===== Dashboard =====
function hasWeakLocalPattern(password) {
  const lower = password.toLowerCase();

  const weakPatterns = [
    "123",
    "1234",
    "12345",
    "123456",
    "abc",
    "abcd",
    "qwerty",
    "asdf",
    "zxcv",
    "password",
    "admin",
  ];

  return weakPatterns.some((pattern) => lower.includes(pattern));
}

function updateCardState(card, isValid) {
  if (!card) return;

  card.classList.toggle("ok", isValid);
  card.classList.toggle("bad", !isValid);
}

function updateDashboard(password) {
  if (!dashboardSection) return;

  if (!password) {
    hideElement(dashboardSection);
    return;
  }

  showElement(dashboardSection);

  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[^a-zA-Z0-9]/.test(password);
  const lengthOk = password.length >= 8;
  const patternOk = !hasWeakLocalPattern(password);

  if (valLength) valLength.textContent = `${password.length} karakter`;
  if (valUpper) valUpper.textContent = hasUpper ? "Var" : "Yok";
  if (valLower) valLower.textContent = hasLower ? "Var" : "Yok";
  if (valDigit) valDigit.textContent = hasDigit ? "Var" : "Yok";
  if (valSpecial) valSpecial.textContent = hasSpecial ? "Var" : "Yok";
  if (valPatterns) valPatterns.textContent = patternOk ? "Temiz" : "Riskli";

  updateCardState(dashCards.upper, hasUpper);
  updateCardState(dashCards.lower, hasLower);
  updateCardState(dashCards.digit, hasDigit);
  updateCardState(dashCards.special, hasSpecial);
  updateCardState(dashCards.patterns, patternOk && lengthOk);
}

// ===== API =====
async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  let data = null;

  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      data?.error ||
      `API isteği başarısız oldu (${response.status})`;

    throw new Error(message);
  }

  return data;
}

async function scorePassword(password) {
  return postJson(SCORE_ENDPOINT, { password });
}

async function explainPassword(password) {
  return postJson(EXPLAIN_ENDPOINT, { password });
}

async function generateSecurePassword() {
  return postJson(GENERATE_ENDPOINT, {
    length: 16,
    use_uppercase: true,
    use_lowercase: true,
    use_digits: true,
    use_special: true,
  });
}

// ===== Response parsing =====
function getScoreFromResponse(scoreData) {
  const rawScore =
    scoreData?.final_score ??
    scoreData?.security_score ??
    scoreData?.score ??
    scoreData?.risk_score ??
    0;

  const numericScore = Number(rawScore);

  if (Number.isNaN(numericScore)) return 0;

  return Math.max(0, Math.min(100, numericScore));
}

function getLevelFromResponse(scoreData, score) {
  if (scoreData?.security_level) return scoreData.security_level;
  if (scoreData?.level) return scoreData.level;

  if (score < 20) return "Çok Zayıf";
  if (score < 40) return "Zayıf";
  if (score < 60) return "Orta";
  if (score < 80) return "Güçlü";
  return "Çok Güçlü";
}

function normalizeList(value) {
  if (!value) return [];

  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === "string") return item;
        if (item?.message) return item.message;
        if (item?.text) return item.text;
        if (item?.details) return item.details;
        if (item?.pattern) return item.pattern;
        return JSON.stringify(item);
      })
      .filter(Boolean);
  }

  if (typeof value === "string") return [value];

  return [];
}

function extractReasons(scoreData, explainData) {
  return [
    ...normalizeList(scoreData?.feedback),
    ...normalizeList(scoreData?.weak_patterns),
    ...normalizeList(scoreData?.patterns),
    ...normalizeList(explainData?.reasons),
    ...normalizeList(explainData?.explanations),
    ...normalizeList(explainData?.details),
    ...normalizeList(explainData?.feedback),
  ];
}

function extractSuggestions(scoreData, explainData) {
  return [
    ...normalizeList(scoreData?.suggestions),
    ...normalizeList(scoreData?.recommendations),
    ...normalizeList(explainData?.suggestions),
    ...normalizeList(explainData?.recommendations),
  ];
}

function extractAlternatives(generateData) {
  return [
    ...normalizeList(generateData?.alternatives),
    ...normalizeList(generateData?.suggested_passwords),
    ...normalizeList(generateData?.suggestions),
  ];
}

// ===== Rendering =====
function renderScore(scoreData, explainData = null) {
  const score = getScoreFromResponse(scoreData);
  const level = getLevelFromResponse(scoreData, score);
  const levelMeta = LEVEL_MAP[level] || LEVEL_MAP["Orta"];

  showElement(resultSection);

  if (securityLevel) {
    securityLevel.textContent = level;
    securityLevel.className = `level ${levelMeta.cls}`;
  }

  if (riskScore) {
    riskScore.textContent = `${Math.round(score)} / 100`;
  }

  if (progressBar) {
    progressBar.style.width = `${score}%`;
    progressBar.className = `progress-bar ${levelMeta.cls}`;
  }

  if (scoreMessage) {
    scoreMessage.textContent =
      scoreData?.message ||
      explainData?.summary ||
      explainData?.message ||
      buildScoreMessage(level, score);
  }

  renderReasons(scoreData, explainData);
  renderSuggestions(scoreData, explainData);
}

function buildScoreMessage(level, score) {
  if (score < 20) return "Bu parola çok zayıf ve kolay tahmin edilebilir.";
  if (score < 40) return "Bu parola zayıf. Daha uzun ve karmaşık hale getirin.";
  if (score < 60) return "Bu parola orta seviyede. Birkaç iyileştirme önerilir.";
  if (score < 80) return "Bu parola güçlü görünüyor.";
  return "Bu parola çok güçlü görünüyor.";
}

function renderReasons(scoreData, explainData) {
  const reasons = [...new Set(extractReasons(scoreData, explainData))];

  clearList(reasonsList);

  if (!reasons.length) {
    hideElement(reasonsSection);
    return;
  }

  reasons.forEach((reason) => appendListItem(reasonsList, reason));
  showElement(reasonsSection);
}

function renderSuggestions(scoreData, explainData) {
  const suggestions = [...new Set(extractSuggestions(scoreData, explainData))];

  clearList(suggestionsList);

  if (!suggestions.length) {
    hideElement(suggestionsSection);
    return;
  }

  suggestions.forEach((suggestion) => appendListItem(suggestionsList, suggestion));
  showElement(suggestionsSection);
}

function renderGeneratedPassword(generateData) {
  const password =
    generateData?.generated_password ||
    generateData?.password ||
    generateData?.secure_password ||
    "";

  if (!password) {
    throw new Error("API parola üretimi için geçerli bir değer döndürmedi.");
  }

  if (generatedPassword) {
    generatedPassword.textContent = password;
  }

  showElement(generatedSection);

  const alternatives = extractAlternatives(generateData);
  clearList(alternativesList);

  if (alternatives.length) {
    alternatives.forEach((item) => appendListItem(alternativesList, item));
    showElement(alternativesSection);
  } else {
    hideElement(alternativesSection);
  }

  if (passwordInput) {
    passwordInput.value = password;
    updateDashboard(password);
  }

  renderScore(generateData, null);
}

// ===== Actions =====
async function analyzePassword() {
  const password = passwordInput ? passwordInput.value.trim() : "";

  if (!password) {
    showToast("Lütfen analiz edilecek bir parola girin.", "error");
    if (passwordInput) passwordInput.focus();
    return;
  }

  try {
    setButtonLoading(analyzeBtn, true, "Analiz ediliyor...", "Analiz Et");

    const [scoreData, explainData] = await Promise.all([
      scorePassword(password),
      explainPassword(password).catch(() => null),
    ]);

    renderScore(scoreData, explainData);
    showToast("Parola analizi tamamlandı.", "success");
  } catch (error) {
    showToast(error.message || "Parola analizi sırasında hata oluştu.", "error");
  } finally {
    setButtonLoading(analyzeBtn, false, "Analiz ediliyor...", "Analiz Et");
  }
}

async function handleGeneratePassword() {
  try {
    setButtonLoading(generateBtn, true, "Üretiliyor...", "Güvenli Parola Üret");

    const generateData = await generateSecurePassword();
    renderGeneratedPassword(generateData);

    showToast("Güvenli parola üretildi.", "success");
  } catch (error) {
    showToast(error.message || "Parola üretimi sırasında hata oluştu.", "error");
  } finally {
    setButtonLoading(generateBtn, false, "Üretiliyor...", "Güvenli Parola Üret");
  }
}

async function copyGeneratedPassword() {
  const text = generatedPassword ? generatedPassword.textContent.trim() : "";

  if (!text) {
    showToast("Kopyalanacak parola bulunamadı.", "error");
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    showToast("Parola panoya kopyalandı.", "success");
  } catch (error) {
    showToast("Kopyalama başarısız oldu.", "error");
  }
}

function togglePasswordVisibility() {
  if (!passwordInput || !toggleBtn) return;

  const isPassword = passwordInput.type === "password";
  passwordInput.type = isPassword ? "text" : "password";
  toggleBtn.textContent = isPassword ? "🙈" : "👁";
}

// ===== Event listeners =====
if (analyzeBtn) {
  analyzeBtn.addEventListener("click", analyzePassword);
}

if (generateBtn) {
  generateBtn.addEventListener("click", handleGeneratePassword);
}

if (copyBtn) {
  copyBtn.addEventListener("click", copyGeneratedPassword);
}

if (toggleBtn) {
  toggleBtn.addEventListener("click", togglePasswordVisibility);
}

if (passwordInput) {
  passwordInput.addEventListener("input", (event) => {
    updateDashboard(event.target.value);
  });

  passwordInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      analyzePassword();
    }
  });
}

// Initial state
hideElement(resultSection);
hideElement(reasonsSection);
hideElement(suggestionsSection);
hideElement(generatedSection);
hideElement(alternativesSection);
hideElement(dashboardSection);