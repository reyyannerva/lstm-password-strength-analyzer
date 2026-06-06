\# Proje Test ve Çalıştırma Rehberi



\## Genel Bakış



Bu proje, LSTM tabanlı parola güvenlik analizi gerçekleştiren bir sistemdir.



\### Özellikler



\* Parola güvenlik skorlama

\* Riskli desen tespiti

\* Güvenlik seviyesi sınıflandırması

\* Güvenli parola üretimi

\* Türkçe karakter desteği

\* REST API servisi

\* Modern web arayüzü

\* Otomatik test altyapısı



\---



\## Kurulum



\### Repoyu İndirme



```bash

git clone https://github.com/reyyannerva/lstm-password-strength-analyzer.git

cd lstm-password-strength-analyzer

```



\### Bağımlılıkları Kurma



```bash

pip install -r requirements.txt

```



\---



\## Testleri Çalıştırma



```bash

python -m pytest

```



Beklenen sonuç:



```text

230 passed

```



\---



\## Backend'i Çalıştırma



```bash

python -m uvicorn src.api.main:app --reload

```



Swagger arayüzü:



```text

http://127.0.0.1:8000/docs

```



\---



\## Frontend'i Çalıştırma



Yeni terminal:



```bash

python -m http.server 5500

```



Tarayıcı:



```text

http://localhost:5500/frontend/index.html

```



\---



\## Örnek Test Senaryoları



\### Çok Zayıf



```text

123456

```



Beklenen: Çok Zayıf



\### Zayıf



```text

password123

```



Beklenen: Zayıf



\### Güçlü



```text

Str0ng!Pass123

```



Beklenen: Güçlü



\### Çok Güçlü



```text

VeryStrong#2026Pass

```



Beklenen: Güçlü veya Çok Güçlü



\### Türkçe Karakter Testi



```text

Şertgg45325.

```



Beklenen:



\* Büyük harf tespiti başarılı

\* Türkçe karakter desteği çalışıyor



\---



\## API Endpointleri



\### POST /score



Parola güvenlik skorunu döndürür.



\### POST /explain



Risk nedenleri ve önerileri döndürür.



\### POST /generate



Güvenli parola üretir.



\---



\## Doğrulama Sonucu



Teslim öncesi tüm otomatik testler çalıştırılmıştır.



```text

230 passed

```



Sistem bileşenleri:



\* Backend ✅

\* Frontend ✅

\* API ✅

\* Güvenlik Analizi ✅

\* Güvenli Parola Üretimi ✅

\* Türkçe Karakter Desteği ✅



