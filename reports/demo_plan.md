# Demo Planı

## Demo Amacı

Bu demo kapsamında sistemin parola analizi, açıklama üretimi ve güvenli parola oluşturma özellikleri gösterilecektir.

---

# Senaryo 1: Çok Zayıf Parola

Girilecek parola:

```text
123456
```

Beklenen sonuç:

* Çok Zayıf güvenlik seviyesi
* Düşük skor
* Zayıf desen uyarıları
* Güvenlik önerileri

Gösterilecek özellikler:

* Pattern detection
* Risk scoring
* Explain endpoint

---

# Senaryo 2: Yaygın Parola

Girilecek parola:

```text
password123
```

Beklenen sonuç:

* Yaygın parola kelimesi tespiti
* Ardışık karakter tespiti
* Düşük güvenlik puanı

Gösterilecek özellikler:

* Common word detection
* Explain system

---

# Senaryo 3: Orta Güçlü Parola

Girilecek parola:

```text
Password123
```

Beklenen sonuç:

* Orta seviyede skor
* Özel karakter önerisi

Gösterilecek özellikler:

* Rule based analysis
* Security feedback

---

# Senaryo 4: Güçlü Parola

Girilecek parola:

```text
Str0ng!Pass123
```

Beklenen sonuç:

* Güçlü veya Çok Güçlü skor
* Az sayıda uyarı

Gösterilecek özellikler:

* Hybrid risk scorer
* Frontend API integration

---

# Senaryo 5: Güvenli Parola Üretimi

Adımlar:

1. Güvenli Parola Üret butonuna basılır.
2. Sistem yeni parola üretir.
3. Üretilen parola otomatik analiz edilir.

Beklenen sonuç:

* Güçlü parola üretimi
* Yüksek skor
* Başarılı analiz

---

# Demo Akışı

1. Sistem açılır.
2. Frontend gösterilir.
3. Zayıf parola analizi yapılır.
4. Açıklama sistemi gösterilir.
5. Güçlü parola analizi yapılır.
6. Güvenli parola üretimi gösterilir.
7. Swagger API ekranı gösterilir.
8. Test ve CI/CD süreci anlatılır.

Tahmini süre: 5-7 dakika.
