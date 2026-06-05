# 🔐 LSTM Password Strength Analyzer

LSTM destekli parola güvenliği analiz sistemi, zayıf parola desen tespiti ve güvenli parola öneri platformu.

---

# 📖 Proje Hakkında

LSTM Password Strength Analyzer, kullanıcıların oluşturduğu parolaların güvenlik seviyesini değerlendirmek, zayıf parola desenlerini tespit etmek ve daha güvenli parola önerileri sunmak amacıyla geliştirilmiş bir siber güvenlik projesidir.

Sistem, geleneksel kural tabanlı parola analiz yöntemlerini makine öğrenmesi tabanlı tahmin edilebilirlik yaklaşımıyla birleştirmektedir. Böylece yalnızca parola uzunluğu ve karakter çeşitliliği değil, aynı zamanda parolanın içerdiği riskli örüntüler de analiz edilmektedir.

Proje kapsamında geliştirilen FastAPI tabanlı servisler sayesinde parola analizi, açıklama üretimi ve güvenli parola oluşturma işlemleri REST API üzerinden gerçekleştirilebilmektedir.

---

# 🎯 Proje Amaçları

Bu projenin temel amaçları:

* Parolaların güvenlik seviyesini analiz etmek
* Zayıf parola desenlerini tespit etmek
* Kullanıcıya açıklanabilir geri bildirim sağlamak
* Güvenli parola önerileri üretmek
* REST API servisleri geliştirmek
* Modern bir web arayüzü sunmak
* Otomatik test ve CI/CD süreçlerini uygulamak
* LSTM tabanlı tahmin edilebilirlik analizine altyapı hazırlamak

---

# 🚀 Özellikler

## Parola Güvenlik Analizi

Sistem aşağıdaki kriterleri değerlendirir:

* Parola uzunluğu
* Büyük harf kullanımı
* Küçük harf kullanımı
* Sayı kullanımı
* Özel karakter kullanımı
* Karakter çeşitliliği

---

## Zayıf Desen Tespiti

Sistem aşağıdaki riskli desenleri algılar:

* Ardışık karakterler (`123`, `abc`)
* Klavye desenleri (`qwerty`, `asdf`)
* Tekrarlayan karakterler (`aaa`, `111`)
* Yaygın parola kelimeleri
* Yaygın yıl ifadeleri
* Sadece harflerden oluşan parolalar
* Sadece rakamlardan oluşan parolalar

---

## Güvenli Parola Üretimi

Sistem:

* Güçlü parola üretir
* Riskli desenleri filtreler
* Karakter çeşitliliğini garanti eder
* İstenilen uzunlukta parola oluşturabilir

---

## Açıklama ve Öneri Sistemi

Her parola için:

* Güvenlik puanı
* Güvenlik seviyesi
* Riskli desen açıklamaları
* Güvenlik önerileri

üretilmektedir.

---

# 🏗 Sistem Mimarisi

```text
Frontend
    │
    ▼
FastAPI Backend
    │
    ├── Score Endpoint
    ├── Explain Endpoint
    ├── Generate Endpoint
    │
    ▼
Security Layer
    │
    ├── Pattern Detection
    ├── Hybrid Risk Scorer
    ├── Rule Analysis
    └── Password Generator
```

---

# 📂 Proje Yapısı

```text
lstm-password-strength-analyzer
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── src/
│   ├── api/
│   ├── security/
│   ├── data/
│   └── model/
│
├── tests/
│
├── reports/
│
├── .github/
│   └── workflows/
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Kurulum

## Repository'yi Klonlayın

```bash
git clone https://github.com/reyyannerva/lstm-password-strength-analyzer.git
cd lstm-password-strength-analyzer
```

## Sanal Ortam Oluşturun

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

## Bağımlılıkları Kurun

```bash
pip install -r requirements.txt
```

---

# ▶️ Uygulamayı Çalıştırma

Backend:

```bash
uvicorn src.api.main:app --reload
```

Swagger Arayüzü:

```text
http://127.0.0.1:8000/docs
```

Frontend:

```text
frontend/index.html
```

dosyasını tarayıcıda açabilirsiniz.

---

# 🔌 API Endpointleri

## GET /health

Sistemin çalışıp çalışmadığını kontrol eder.

---

## POST /score

Parola güvenlik puanı üretir.

Örnek:

```json
{
  "password": "Str0ng!Pass123"
}
```

---

## POST /explain

Parola için açıklama ve öneriler üretir.

Örnek:

```json
{
  "password": "password123"
}
```

---

## POST /generate

Güvenli parola üretir.

Örnek:

```json
{
  "length": 16
}
```

---

# 🧪 Testler

Tüm testleri çalıştırmak için:

```bash
python -m pytest
```

API testleri:

```bash
python -m pytest tests/test_api.py
```

---

# 🔄 CI/CD

Proje GitHub Actions ile entegredir.

Aşağıdaki durumlarda testler otomatik çalıştırılır:

* Pull Request oluşturulduğunda
* dev branch'ine push yapıldığında
* main branch'ine push yapıldığında

Başarısız test durumunda workflow hata verir.

---

# 👥 Proje Ekibi

| Üye    | Sorumluluk                                      |
| ------ | ----------------------------------------------- |
| Reyyan | Proje yönetimi, entegrasyon, backend geliştirme |
| Burcu  | Frontend geliştirme, kullanıcı arayüzü          |
| Merve  | Veri işleme, testler ve analiz modülleri        |

---

# 📄 Lisans

Bu proje akademik amaçlarla geliştirilmiştir.
