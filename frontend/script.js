const API_BASE = "http://localhost:8000";

const SCORE_ENDPOINT = `${API_BASE}/score`;
const EXPLAIN_ENDPOINT = `${API_BASE}/explain`;
const GENERATE_ENDPOINT = `${API_BASE}/generate`;

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
  "Çok Zayıf": { cls: "very-weak", fallbackBar: 5 },
  "Zayıf": { cls: "weak", fallbackBar: 25 },
  "Orta": { cls: "medium", fallbackBar: 50 },
  "Güçlü": { cls: "strong", fallbackBar: 75 },
  "Çok Güçlü": { cls: "very-strong", fallbackBar: 95 },
};

const TURKISH_UPPERCASE_REGEX = /[A-ZÇĞİÖŞÜ]/;
const TURKISH_LOWERCASE_REGEX = /[a-zçğıöşü]/;
const DIGIT_REGEX = /\d/;
const SPECIAL_REGEX = /[^A-ZÇĞİÖŞÜa-zçğıöşü0-9]/;

const DEFAULT_GENERATED_PASSWORD_LENGTH = 16;

function safeText(value, fallback = "") {
  if (value === null || value === undefined) return fallback;
  return String(value);
}

function clampNumber(value, min = 0, max = 100) {
  const number = Number(value);
  if (!Number.isFinite(number)) return min;
  return Math.max(min, Math.min(max, number));
}

function showElement(element) {
  if (!element) return;
  element.classList.remove("hidden");
}

function hideElement(element) {
  if (!element) return;
  element.classList.add("hidden");
}

function clearList(element) {
  if (!element) return;
  element.innerHTML = "";
}

function appendListItem(element, text) {
  if (!element) return;

  const normalizedText = safeText(text).trim();
  if (!normalizedText) return;

  const li = document.createElement("li");
  li.textContent = normalizedText;
  element.appendChild(li);
}

function uniqueList(items) {
  return [...new Set(items.map((item) => safeText(item).trim()).filter(Boolean))];
}

function setButtonLoading(button, isLoading, loadingText, defaultText) {
  if (!button) return;
  button.disabled = Boolean(isLoading);
  button.textContent = isLoading ? loadingText : defaultText;
}

function showToast(message, type = "info") {
  const normalizedMessage = safeText(message, "Bilgi").trim();

  if (!toastContainer) {
    console.log(`[${type}] ${normalizedMessage}`);
    return;
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = normalizedMessage;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);
}

function applyTheme(theme) {
  if (!themeToggle) return;

  const normalizedTheme = theme === "light" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", normalizedTheme);
  themeToggle.textContent = normalizedTheme === "dark" ? "🌙" : "☀️";
  localStorage.setItem("theme", normalizedTheme);
}

function hasUppercase(password) {
  return TURKISH_UPPERCASE_REGEX.test(safeText(password));
}

function hasLowercase(password) {
  return TURKISH_LOWERCASE_REGEX.test(safeText(password));
}

function hasDigit(password) {
  return DIGIT_REGEX.test(safeText(password));
}

function hasSpecial(password) {
  return SPECIAL_REGEX.test(safeText(password));
}

function hasWeakLocalPattern(password) {
  const lower = safeText(password).toLowerCase();

  const weakPatterns = [
    "123",
    "1234",
    "12345",
    "123456",
    "123456789",
    "abc",
    "abcd",
    "qwerty",
    "asdf",
    "zxcv",
    "password",
    "parola",
    "admin",
    "test",
    "root",
    "login",
    "welcome",
  ];

  return weakPatterns.some((pattern) => lower.includes(pattern));
}

function updateCardState(card, isValid) {
  if (!card) return;
  card.classList.toggle("ok", Boolean(isValid));
  card.classList.toggle("bad", !Boolean(isValid));
}

function updateDashboard(password) {
  if (!dashboardSection) return;

  const currentPassword = safeText(password);

  if (!currentPassword) {
    hideElement(dashboardSection);
    return;
  }

  showElement(dashboardSection);

  const upper = hasUppercase(currentPassword);
  const lower = hasLowercase(currentPassword);
  const digit = hasDigit(currentPassword);
  const special = hasSpecial(currentPassword);
  const patternClean = !hasWeakLocalPattern(currentPassword);

  if (valLength) valLength.textContent = `${currentPassword.length} karakter`;
  if (valUpper) valUpper.textContent = upper ? "Var" : "Yok";
  if (valLower) valLower.textContent = lower ? "Var" : "Yok";
  if (valDigit) valDigit.textContent = digit ? "Var" : "Yok";
  if (valSpecial) valSpecial.textContent = special ? "Var" : "Yok";
  if (valPatterns) valPatterns.textContent = patternClean ? "Temiz" : "Riskli";

  updateCardState(dashCards.upper, upper);
  updateCardState(dashCards.lower, lower);
  updateCardState(dashCards.digit, digit);
  updateCardState(dashCards.special, special);
  updateCardState(dashCards.patterns, patternClean);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
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
    length: DEFAULT_GENERATED_PASSWORD_LENGTH,
    use_uppercase: true,
    use_lowercase: true,
    use_digits: true,
    use_special: true,
  });
}

function getScoreFromResponse(scoreData) {
  if (!scoreData || typeof scoreData !== "object") return 0;

  /*
    ÖNEMLİ:
    API şu alanları döndürebiliyor:

    strength_score: güvenlik skoru, UI'da gösterilecek doğru alan
    risk_score: risk skoru, yüksekse parola kötü demektir
    security_level: metinsel seviye

    Bu yüzden risk_score asla ilk tercih edilmez.
    123456 için API:
    strength_score = 0
    risk_score = 100
    security_level = Çok Zayıf

    UI'da gösterilmesi gereken:
    0 / 100
  */

  if (scoreData.final_score !== undefined && scoreData.final_score !== null) {
    return clampNumber(scoreData.final_score);
  }

  if (scoreData.strength_score !== undefined && scoreData.strength_score !== null) {
    return clampNumber(scoreData.strength_score);
  }

  if (scoreData.security_score !== undefined && scoreData.security_score !== null) {
    return clampNumber(scoreData.security_score);
  }

  if (scoreData.score !== undefined && scoreData.score !== null) {
    return clampNumber(scoreData.score);
  }

  if (scoreData.password_score !== undefined && scoreData.password_score !== null) {
    return clampNumber(scoreData.password_score);
  }

  if (scoreData.risk_score !== undefined && scoreData.risk_score !== null) {
    return clampNumber(100 - Number(scoreData.risk_score));
  }

  return 0;
}

function normalizeSecurityLevel(level) {
  const rawLevel = safeText(level).trim();

  const aliases = {
    "very weak": "Çok Zayıf",
    very_weak: "Çok Zayıf",
    "çok zayıf": "Çok Zayıf",
    "cok zayif": "Çok Zayıf",

    weak: "Zayıf",
    zayıf: "Zayıf",
    zayif: "Zayıf",

    medium: "Orta",
    orta: "Orta",

    strong: "Güçlü",
    güçlü: "Güçlü",
    guclu: "Güçlü",

    "very strong": "Çok Güçlü",
    very_strong: "Çok Güçlü",
    "çok güçlü": "Çok Güçlü",
    "cok guclu": "Çok Güçlü",
  };

  const key = rawLevel.toLowerCase();
  return aliases[key] || rawLevel;
}

function getLevelFromScore(score) {
  const normalizedScore = clampNumber(score);

  if (normalizedScore < 20) return "Çok Zayıf";
  if (normalizedScore < 40) return "Zayıf";
  if (normalizedScore < 60) return "Orta";
  if (normalizedScore < 80) return "Güçlü";
  return "Çok Güçlü";
}

function getLevelFromResponse(scoreData, score) {
  const apiLevel =
    scoreData?.security_level ||
    scoreData?.level ||
    scoreData?.strength_level ||
    scoreData?.password_level;

  const normalizedApiLevel = normalizeSecurityLevel(apiLevel);

  if (LEVEL_MAP[normalizedApiLevel]) {
    return normalizedApiLevel;
  }

  return getLevelFromScore(score);
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
        if (item?.detail) return item.detail;
        if (item?.pattern) return item.pattern;
        if (item?.reason) return item.reason;
        if (item?.suggestion) return item.suggestion;

        try {
          return JSON.stringify(item);
        } catch (error) {
          return String(item);
        }
      })
      .filter(Boolean);
  }

  if (typeof value === "string") return [value];

  if (typeof value === "object") {
    return Object.values(value)
      .flatMap((item) => normalizeList(item))
      .filter(Boolean);
  }

  return [];
}

function extractReasons(scoreData, explainData) {
  return uniqueList([
    ...normalizeList(scoreData?.feedback),
    ...normalizeList(scoreData?.weak_patterns),
    ...normalizeList(scoreData?.patterns),
    ...normalizeList(scoreData?.risk_reasons),
    ...normalizeList(scoreData?.reasons),
    ...normalizeList(scoreData?.details),

    ...normalizeList(explainData?.reasons),
    ...normalizeList(explainData?.explanations),
    ...normalizeList(explainData?.details),
    ...normalizeList(explainData?.feedback),
    ...normalizeList(explainData?.risk_reasons),
  ]);
}

function extractSuggestions(scoreData, explainData) {
  return uniqueList([
    ...normalizeList(scoreData?.suggestions),
    ...normalizeList(scoreData?.recommendations),
    ...normalizeList(scoreData?.advice),
    ...normalizeList(scoreData?.improvements),

    ...normalizeList(explainData?.suggestions),
    ...normalizeList(explainData?.recommendations),
    ...normalizeList(explainData?.advice),
    ...normalizeList(explainData?.improvements),
  ]);
}

function extractAlternatives(generateData) {
  return uniqueList([
    ...normalizeList(generateData?.alternatives),
    ...normalizeList(generateData?.suggested_passwords),
    ...normalizeList(generateData?.suggestions),
    ...normalizeList(generateData?.passwords),
  ]);
}

function buildScoreMessage(level, score) {
  const normalizedScore = clampNumber(score);

  if (level === "Çok Zayıf" || normalizedScore < 20) {
    return "Bu parola çok zayıf. Hemen değiştirin.";
  }

  if (level === "Zayıf" || normalizedScore < 40) {
    return "Bu parola zayıf. Daha güçlü bir parola seçin.";
  }

  if (level === "Orta" || normalizedScore < 60) {
    return "Parola orta düzeyde güvenli. İyileştirilebilir.";
  }

  if (level === "Güçlü" || normalizedScore < 80) {
    return "Parola güçlü.";
  }

  return "Parola çok güçlü.";
}

function renderReasons(scoreData, explainData) {
  const reasons = extractReasons(scoreData, explainData);

  clearList(reasonsList);

  if (!reasons.length) {
    hideElement(reasonsSection);
    return;
  }

  reasons.forEach((reason) => appendListItem(reasonsList, reason));
  showElement(reasonsSection);
}

function renderSuggestions(scoreData, explainData) {
  const suggestions = extractSuggestions(scoreData, explainData);

  clearList(suggestionsList);

  if (!suggestions.length) {
    hideElement(suggestionsSection);
    return;
  }

  suggestions.forEach((suggestion) => appendListItem(suggestionsList, suggestion));
  showElement(suggestionsSection);
}

function renderScore(scoreData, explainData = null) {
  const score = getScoreFromResponse(scoreData);
  const level = getLevelFromResponse(scoreData, score);
  const levelMeta = LEVEL_MAP[level] || LEVEL_MAP[getLevelFromScore(score)] || LEVEL_MAP["Orta"];

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

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(currentTheme === "dark" ? "light" : "dark");
  });
}

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

applyTheme(localStorage.getItem("theme") || "dark");

hideElement(resultSection);
hideElement(reasonsSection);
hideElement(suggestionsSection);
hideElement(generatedSection);
hideElement(alternativesSection);
hideElement(dashboardSection);