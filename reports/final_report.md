# LSTM Password Strength Analyzer Projesi Final Raporu

## 1. Giriş

Parolalar günümüzde en yaygın kullanılan kimlik doğrulama yöntemlerinden biridir. Ancak kullanıcıların zayıf, tahmin edilmesi kolay veya tekrar eden parolalar kullanması güvenlik açıklarına neden olmaktadır. Özellikle sözlük saldırıları, kaba kuvvet saldırıları ve parola sızıntılarından elde edilen veriler, zayıf parola kullanımının halen önemli bir siber güvenlik problemi olduğunu göstermektedir.

Bu proje kapsamında kullanıcı parolalarının güvenlik seviyesini değerlendiren, zayıf parola desenlerini tespit eden ve güvenli parola önerileri sunan bir sistem geliştirilmiştir. Sistem hem kural tabanlı analiz yöntemlerinden hem de LSTM tabanlı tahmin edilebilirlik yaklaşımından yararlanacak şekilde tasarlanmıştır.

---

# 2. Proje Amacı

Projenin temel amacı kullanıcıların oluşturduğu parolaların güvenlik seviyesini analiz etmek ve daha güçlü parola kullanımı konusunda rehberlik sağlamaktır.

Bu kapsamda aşağıdaki hedefler belirlenmiştir:

* Parola güvenlik seviyesinin ölçülmesi
* Riskli parola desenlerinin tespit edilmesi
* Kullanıcıya açıklanabilir geri bildirim verilmesi
* Güvenli parola önerilerinin üretilmesi
* REST API servislerinin geliştirilmesi
* Web tabanlı kullanıcı arayüzünün oluşturulması
* Otomatik test ve CI/CD süreçlerinin uygulanması

---

# 3. Sistem Mimarisi

Sistem dört temel katmandan oluşmaktadır.

## 3.1 Frontend Katmanı

Frontend katmanı kullanıcı ile sistem arasındaki etkileşimi sağlamaktadır.

Bu katmanda:

* Parola girişi
* Güvenlik puanı gösterimi
* Açıklama ve önerilerin görüntülenmesi
* Güvenli parola üretimi

işlemleri gerçekleştirilmektedir.

---

## 3.2 API Katmanı

Backend servisleri FastAPI kullanılarak geliştirilmiştir.

Sistem aşağıdaki endpointleri sunmaktadır:

| Endpoint       | Açıklama                  |
| -------------- | ------------------------- |
| GET /health    | Servis durum kontrolü     |
| POST /score    | Parola puanlama           |
| POST /explain  | Açıklama ve öneri üretimi |
| POST /generate | Güvenli parola üretimi    |

---

## 3.3 Güvenlik Analiz Katmanı

Bu katman parola güvenlik analizlerinden sorumludur.

Uygulanan kontroller:

* Uzunluk kontrolü
* Büyük harf kontrolü
* Küçük harf kontrolü
* Sayı kontrolü
* Özel karakter kontrolü
* Karakter çeşitliliği analizi

Ayrıca parola içerisinde bulunan riskli örüntüler de analiz edilmektedir.

---

## 3.4 Desen Tespit Katmanı

Bu modül aşağıdaki zayıf parola desenlerini tespit etmektedir:

* Ardışık karakter dizileri
* Klavye desenleri
* Tekrarlayan karakterler
* Yaygın parola kelimeleri
* Yaygın yıl ifadeleri
* Sadece rakamlardan oluşan parolalar
* Sadece harflerden oluşan parolalar

Bu desenler parola skorunun hesaplanmasında kullanılmaktadır.

---

# 4. Geliştirilen Modüller

## 4.1 Veri Hazırlama Modülü

Parola verilerinin işlenmesi amacıyla veri yükleme ve ön işleme bileşenleri geliştirilmiştir.

Bu modül:

* Veri yükleme
* Temizleme
* Tokenizasyon
* Eğitim verisi hazırlama

işlemlerini gerçekleştirmektedir.

---

## 4.2 Hybrid Risk Scorer

Hybrid Risk Scorer modülü projenin temel bileşenlerinden biridir.

Bu modül:

* Kural tabanlı analiz
* Desen analizi
* Güvenlik puanı üretimi
* Güvenlik seviyesi belirleme

işlemlerini gerçekleştirmektedir.

Sonuç olarak kullanıcıya 0 ile 100 arasında bir güvenlik puanı sunulmaktadır.

---

## 4.3 Açıklama Sistemi

Parola analizi sonucunda kullanıcıya yalnızca puan verilmemekte, aynı zamanda puanın neden oluştuğu açıklanmaktadır.

Örnek açıklamalar:

* Yaygın parola kelimesi içeriyor
* Ardışık karakter dizisi içeriyor
* Özel karakter eksik
* Büyük harf eksik

Bu yaklaşım kullanıcı deneyimini geliştirmektedir.

---

## 4.4 Güvenli Parola Üretici

Sistem güvenli parola üretme yeteneğine sahiptir.

Üretilen parolalar:

* Büyük harf içerir
* Küçük harf içerir
* Sayı içerir
* Özel karakter içerir
* Riskli desenlerden kaçınır

Bu sayede kullanıcılara doğrudan güvenli parola alternatifleri sunulmaktadır.

---

# 5. Test Süreci

Proje kapsamında birim testleri ve API testleri geliştirilmiştir.

Test edilen bileşenler:

* Pattern Detection Modülü
* Rules Modülü
* Risk Scorer Modülü
* Password Generator Modülü
* API Endpointleri

Gerçekleştirilen testler başarıyla tamamlanmıştır.

---

# 6. Sürekli Entegrasyon (CI/CD)

Proje için GitHub Actions tabanlı CI süreci kurulmuştur.

Sistem aşağıdaki durumlarda otomatik olarak çalışmaktadır:

* Pull Request oluşturulduğunda
* Dev branch'ine push yapıldığında
* Main branch'ine push yapıldığında

Bu süreç sayesinde hatalı kodların projeye dahil edilmesi engellenmektedir.

---

# 7. Elde Edilen Sonuçlar

Proje sonunda aşağıdaki çıktılar elde edilmiştir:

* Parola güvenlik analiz sistemi
* Zayıf desen tespit sistemi
* Güvenli parola üretici
* REST API servisleri
* Frontend kullanıcı arayüzü
* Otomatik test altyapısı
* GitHub Actions CI süreci

Sistem başarılı şekilde çalışmakta ve kullanıcıya anlamlı güvenlik geri bildirimleri sunabilmektedir.

---

# 8. Karşılaşılan Zorluklar

Geliştirme sürecinde özellikle:

* Branch yönetimi
* Merge conflict çözümü
* Frontend-backend entegrasyonu
* Skor kalibrasyonu
* API testlerinin standartlaştırılması

konularında çeşitli teknik zorluklarla karşılaşılmıştır.

Bu sorunlar ekip çalışması ve sürüm kontrol süreçleri kullanılarak çözülmüştür.

---

# 9. Gelecek Çalışmalar

Projenin ilerleyen sürümlerinde aşağıdaki geliştirmeler planlanmaktadır:

* Tam eğitimli LSTM model entegrasyonu
* Daha büyük parola veri kümeleri ile eğitim
* Transformer tabanlı modellerin kullanılması
* Kullanıcı bazlı kişiselleştirilmiş parola önerileri
* Çok dilli destek
* Gelişmiş güvenlik raporları

---

# 10. Sonuç

Bu proje kapsamında parola güvenliğinin analiz edilmesi, zayıf parola desenlerinin tespit edilmesi ve güvenli parola önerilerinin üretilmesi amacıyla bütünleşik bir sistem geliştirilmiştir.

Geliştirilen sistem; frontend, backend, güvenlik analizi, parola üretimi, test altyapısı ve CI/CD süreçlerini içeren uçtan uca çalışan bir çözüm sunmaktadır. Proje hedeflerinin büyük bölümü başarıyla gerçekleştirilmiş ve gelecekte geliştirilebilecek sağlam bir temel oluşturulmuştur.
