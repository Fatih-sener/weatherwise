# WeatherWise AI Assistant

Anadolu Hackathon 2026, Case 3 (WeatherWise) için geliştirilen hava durumu asistanı.

Seçilen şehrin anlık hava durumunu alır. Makine öğrenmesi modelleriyle şemsiye gerekip gerekmediğine, ne giyileceğine ve dışarı çıkmaya uygun olup olmadığına karar verir. Bu kararları Claude API ile kısa ve doğal bir öneri cümlesine dönüştürür.

> **English:** A weather assistant built for Anadolu Hackathon 2026 (Case 3). It fetches live weather data, uses four scikit-learn / XGBoost classifiers to decide on umbrella, clothing and outdoor suitability, and turns those decisions into a short natural-language recommendation with the Claude API. Frontend: Streamlit. Backend: Flask.

## Nasıl çalışıyor

```
Open-Meteo (anlık hava, 7 günlük tahmin, hava kalitesi)
        │
        ▼
Streamlit panosu (app.py) ──POST /get_prompt──▶ Flask servisi (flask_app.py)
                                                    │
                                    Katman 1: ML kararları (inference.py)
                                    Katman 2: İstem hazırlama (build_prompt)
                                    Katman 3: Claude API ile öneri metni
```

**Katman 1 – Makine öğrenmesi modelleri**

| Model | Soru | Yöntem |
|---|---|---|
| Şemsiye | Şemsiye gerekli mi? | XGBoost, ikili sınıflandırma |
| Kıyafet | Ne giyilmeli? (8 sınıf) | Random Forest, çok sınıflı |
| Uygunluk | Dışarı çıkmaya uygun mu? | Gradient Boosting, ikili sınıflandırma |
| Hava koşulu | Sensör verisine göre hava ne durumda? | Random Forest, çok sınıflı |

Hava koşulu modeli bulunamazsa rakıma göre kar eşiği hesaplayan kural tabanlı bir yedek devreye girer. Konfor skoru (0–100) sıcaklık, yağış, rüzgâr ve nemden kural tabanlı hesaplanır.

**Katman 2 – İstem hazırlama:** Model kararları ve hava verisi, Claude'a verilecek kısa bir yönergeye dönüştürülür. Ham sayıların tekrar edilmemesi ve cevabın 2–3 cümle olması istenir.

**Katman 3 – Claude API:** Yönergeye göre kullanıcıya doğal dilde öneri üretir.

## Kurulum

Python 3.10 veya üzeri gerekir.

```bash
pip install -r requirements.txt
```

### Veri seti

Modeller hackathon organizasyonunun verdiği **sentetik veri setiyle** eğitildi (10 istasyon, 43.440 saatlik kayıt). Veri seti organizasyona ait olduğu için bu depoda yok. Eğitim için şu dosyaları `data/` klasörüne koyun:

- `activity_recommendations.csv`
- `hourly_observations.csv`

### Modelleri eğitme

```bash
python train_models.py            # şemsiye, kıyafet ve uygunluk modelleri
python train_condition_model.py   # hava koşulu modeli
```

Eğitilen modeller `models/` klasörüne kaydedilir.

### Çalıştırma

Claude API anahtarı koda yazılmaz, ortam değişkeninden okunur:

```bash
# Linux / macOS
export ANTHROPIC_API_KEY="anahtarınız"
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="anahtarınız"
```

İki ayrı terminalde:

```bash
python flask_app.py      # ML servisi: http://127.0.0.1:5000
streamlit run app.py     # Pano
```

## Dosyalar

| Dosya | İçerik |
|---|---|
| `app.py` | Streamlit panosu, şehir seçimi, sonuçların gösterimi |
| `flask_app.py` | ML servisi (`/get_prompt`, `/health`) ve Claude çağrısı |
| `inference.py` | Modellerin yüklenmesi, tahmin, konfor skoru, istem |
| `condition_detector.py` | Hava koşulu tespiti ve simgeler |
| `data_module/weather_api.py` | Open-Meteo'dan hava ve hava kalitesi verisi |
| `ui_module/` | Pano bileşenleri ve arka plan stili |
| `train_models.py`, `train_condition_model.py` | Model eğitimi |
| `llm_layer.py` | Katmanların komut satırından denenmesi için yardımcı |

## Teknolojiler

Python · scikit-learn · XGBoost · pandas · Flask · Streamlit · Claude API · Open-Meteo API

## Geliştiren

Fatih Şener
