Güvenlik Analiz Raporu

Proje Özeti



Bu proje, parola gücünü hibrit bir yaklaşımla analiz eder. Sistem şu bileşenleri birlikte kullanır:



Kural tabanlı parola doğrulama

Zayıf desen tespiti

Hibrit risk skorlama

Karakter tabanlı LSTM dil modeli

Açıklanabilir güvenlik önerileri



Amaç; zayıf parolaları tespit etmek, parolanın tahmin edilebilirliğini değerlendirmek ve kullanıcıya uygulanabilir güvenlik önerileri sunmaktır.



Zayıf Desen Tespiti



Sistem, parolalarda sık görülen farklı zayıf desen kategorilerini tespit eder.



Yaygın Parola Kelimeleri



Örnekler:



password

admin

letmein

welcome

qwerty



Bu desenler, sızdırılmış parola veri kümelerinde sık görüldüğü için yüksek riskli kabul edilir.



Klavye Desenleri



Örnekler:



qwerty

asdf

qaz

123456

abcdef



Klavye düzeninden oluşan desenler kolay tahmin edilebilir ve parolanın güvenliğini azaltır.



Ardışık Karakterler



Örnekler:



abc

abcd

123

1234



Ardışık yapılar parolanın karmaşıklığını düşürür ve brute-force/dictionary saldırılarında tahmin edilebilirliği artırır.



Tekrarlayan Karakterler



Örnekler:



aaa

111

zzzz



Tekrarlayan karakterler zayıf parolalarda sık görüldüğü için cezalandırılır.



Yaygın Yıllar



Örnekler:



1999

2000

2024



Yıl ifadeleri kullanıcıların parolalarında sık kullandığı yapılardır ve saldırganlar için güçlü tahmin ipuçları oluşturabilir.



Tarih Desenleri



Örnekler:



01012024

15051999



Tarih benzeri sayısal yapılar, kişisel bilgiye dayalı olabileceği için zayıf desen olarak değerlendirilir.



Telefon Numarası Benzeri Desenler



Örnekler:



5551234567

5329876543



Telefon numarasına benzeyen yapılar parolanın tahmin edilebilirliğini artırır.



Yaygın İsimler



Örnekler:



ahmet123

mehmet123

john123



İsimler kullanıcılar tarafından sık tercih edildiği için parola güvenliğini azaltan desenler arasında değerlendirilir.



Hibrit Risk Skorlama Mantığı



Sistemde nihai güvenlik skoru hibrit bir yaklaşımla hesaplanır.



Kural Tabanlı Özellikler



Kural tabanlı bileşen şu kriterleri değerlendirir:



Parola uzunluğu

Büyük harf kullanımı

Küçük harf kullanımı

Rakam kullanımı

Özel karakter kullanımı

Karakter çeşitliliği

Zayıf desen cezaları

LSTM Bileşeni



LSTM modeli, parolayı karakter seviyesinde bir dizi olarak değerlendirir ve parolanın tahmin edilebilirliği hakkında ek bir sinyal sağlar.



Tahmin edilmesi daha zor olan parolalar daha güçlü kabul edilir.



Nihai Skor



Nihai skor şu bileşenlerin birleşimiyle hesaplanır:



Kural tabanlı skor

Opsiyonel LSTM skoru



Skor aralıkları:



0–19 → Çok Zayıf

20–39 → Zayıf

40–59 → Orta

60–79 → Güçlü

80–100 → Çok Güçlü

LSTM Değerlendirmesi



Eğitim ve değerlendirme süreci aşağıdaki metrikleri destekler:



Training Loss

Validation Loss

Training Perplexity

Validation Perplexity

Validation Accuracy



Üretilen eğitim grafikleri:



experiments/training\_loss.png

experiments/training\_perplexity.png

experiments/validation\_accuracy.png



Bu metrikler, modelin eğitim sürecindeki öğrenme davranışını ve validation verisi üzerindeki genelleme performansını değerlendirmek için kullanılır.



Güvenlik Önerileri



Sistem kullanıcıya aşağıdaki güvenlik önerilerini sunar:



En az 12 karakter uzunluğunda parola kullanın.

Büyük ve küçük harfleri birlikte kullanın.

Rakam ve özel karakter ekleyin.

İsim, tarih, telefon numarası ve yaygın kelimelerden kaçının.

Klavye desenleri ve ardışık karakterler kullanmayın.

Mümkünse rastgele oluşturulmuş parolalar tercih edin.

Her servis için farklı parola kullanın.

Çok faktörlü kimlik doğrulamayı etkinleştirin.

Sonuç



Geliştirilen güvenlik sistemi, geleneksel parola kalite analizini makine öğrenmesi tabanlı tahmin edilebilirlik analiziyle birleştirir.



Hibrit mimari, parola değerlendirmesini daha kapsamlı hale getirirken kullanıcıya açıklanabilir ve uygulanabilir geri bildirimler sunar. Genişletilmiş desen tespiti, kalibre edilmiş skor sistemi ve LSTM değerlendirme metrikleri sayesinde proje daha güçlü ve bütüncül bir parola güvenliği analiz yapısına sahip olmuştur.

