# 🔐 LSTM Password Strength Analyzer

LSTM tabanlı parola tahmin edilebilirlik analizi ve akıllı güvenli parola öneri sistemi.

## 📌 Proje Hakkında

Bu proje, kullanıcıların oluşturduğu parolaların güvenlik seviyesini analiz etmek ve daha güçlü parola önerileri sunmak amacıyla geliştirilmektedir.

Sistem, geçmiş parola örüntülerini öğrenen Long Short-Term Memory (LSTM) tabanlı derin öğrenme modeli kullanarak parolaların tahmin edilebilirlik düzeyini değerlendirecektir.

## 🎯 Proje Amaçları

* Parolaların güvenlik seviyesini analiz etmek
* Tahmin edilmesi kolay parola desenlerini tespit etmek
* LSTM modeli ile parola örüntülerini öğrenmek
* Güvenli parola önerileri üretmek
* Kullanıcı dostu bir web arayüzü sunmak
* API üzerinden parola değerlendirme hizmeti sağlamak

## 🏗️ Sistem Mimarisi

Proje aşağıdaki temel bileşenlerden oluşmaktadır:

### Veri İşleme Katmanı

* Veri temizleme
* Karakter normalizasyonu
* Tokenizasyon
* Eğitim verisi hazırlama

### Yapay Zeka Katmanı

* LSTM tabanlı parola analiz modeli
* Tahmin edilebilirlik skorlama sistemi
* Güvenlik seviyesi sınıflandırması

### Güvenli Parola Öneri Sistemi

* Rastgele parola üretimi
* Desen tabanlı parola analizi
* Güvenlik puanına göre öneriler

### Web ve API Katmanı

* Flask/FastAPI tabanlı servisler
* REST API endpointleri
* Kullanıcı arayüzü

## 👥 Proje Ekibi

| Üye    | Görev                                             |
| ------ | ------------------------------------------------- |
| Reyyan | Veri yönetimi, entegrasyon ve proje koordinasyonu |
| Burcu  | Model geliştirme ve frontend bileşenleri          |
| Merve  | Veri hazırlama, test ve analiz modülleri          |

## 🌿 Git Workflow

Bu projede Git Flow benzeri bir geliştirme modeli kullanılmaktadır.

### Branch Yapısı

```text
main  → Kararlı sürüm
dev   → Ana geliştirme branch'i
feature/* → Görev bazlı geliştirme branch'leri