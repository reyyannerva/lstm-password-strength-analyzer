# lstm-password-strength-analyzer
LSTM tabanlı parola tahmin edilebilirlik analizi ve akıllı güvenli parola öneri sistemi.

## Proje Klasör Yapısı

```
├── data/
│   ├── raw/          # Ham parola veri setleri
│   └── processed/    # Temizlenmiş ve işlenmiş veriler
├── notebooks/        # Keşif ve deney Jupyter notebook'ları
├── src/
│   ├── model/        # LSTM model mimarisi, eğitim ve değerlendirme
│   ├── security/     # Güvenlik motoru, desen tespiti ve parola üretici
│   ├── api/          # FastAPI backend endpointleri
│   └── utils/        # Yardımcı fonksiyonlar
├── frontend/         # HTML/CSS/JS kullanıcı arayüzü
├── tests/            # Birim ve entegrasyon testleri
├── reports/          # Sonuç raporları ve görseller
└── experiments/      # Deney çıktıları ve model kayıtları
```
