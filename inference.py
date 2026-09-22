"""
Katman 2 — Karar Motoru + Prompt Mühendisliği Köprüsü

ml_predict(input_dict)  →  ML kararlarını üretir
build_prompt(input_dict, ml_decisions)  →  LLM için direktif hazırlar

Kullanım:
    from inference import ml_predict, build_prompt
    decisions = ml_predict({"temperature_c": 8, "humidity_pct": 75, ...})
    prompt    = build_prompt(input_data, decisions)
"""

import os
import numpy as np
import joblib
from dataclasses import dataclass
from typing import Optional

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# ─── LAZY MODEL LOADING ───────────────────────────────────────────────────────
_models = {}


def _load(name: str):
    if name not in _models:
        path = os.path.join(MODEL_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{path} bulunamadı. Önce 'python train_models.py' çalıştır."
            )
        _models[name] = joblib.load(path)
    return _models[name]


# ─── KARAR YAPISI ─────────────────────────────────────────────────────────────
@dataclass
class WeatherDecision:
    umbrella_needed: bool  # şemsiye gerekli mi
    umbrella_prob: float  # olasılık 0-1
    clothing: str  # ham kıyafet etiketi
    clothing_en: str  # İngilizce açıklama
    go_outside: bool  # dışarı çıkılır mı
    go_prob: float  # olasılık 0-1
    comfort_score: int  # 0-100 konfor skoru (hesaplanan)


# Kıyafet etiketlerinin İngilizce açıklamaları
CLOTHING_EN = {
    "very_light_clothing_stay_hydrated": "Very light clothing, stay hydrated",
    "t_shirt_comfortable": "T-shirt and comfortable pants",
    "light_breathable_clothing": "Light, breathable clothing",
    "light_jacket_or_sweater": "Light jacket or sweater",
    "long_sleeves_light_layer": "Long sleeves or light layers",
    "warm_jacket_layers": "Warm jacket and layers",
    "winter_coat_scarf_gloves": "Winter coat and scarf",
    "heavy_winter_coat_gloves_hat": "Heavy winter coat and gloves",
}



def _encode_input(raw: dict) -> np.ndarray:
    """
    Ham sözlüğü model feature vektörüne dönüştürür.
    raw dict örneği:
      {
        "temperature_c": 12,
        "feels_like_c": 9,
        "humidity_pct": 72,
        "wind_speed_kmh": 18,
        "precipitation_mm": 2.5,
        "cloud_cover_pct": 60,
        "uv_index": 2,
        "month": 4,
        "hour_of_day": 8,
        "day_of_week": 1,        # 0=Pazartesi
        "is_weekend": 0,
        "season": "spring",      # winter/spring/summer/autumn
        "weather_condition": "drizzle"
      }
    """
    feature_names = _load("feature_names.pkl")
    encoders = _load("label_encoders.pkl")

    row = []
    for feat in feature_names:
        val = raw.get(feat, 0)
        if feat in encoders:
            le = encoders[feat]
            val_str = str(val)
            if val_str in le.classes_:
                val = le.transform([val_str])[0]
            else:
                # Bilinmeyen kategori → en yakın sınıfa fallback
                val = 0
        row.append(float(val))

    return np.array(row).reshape(1, -1)


def _comfort_score(raw: dict) -> int:
    """
    Geleneksel kural tabanlı konfor skoru (0-100).
    ML modellerinden bağımsız, her zaman tutarlı.
    """
    temp = raw.get("temperature_c", 15)
    rain = raw.get("precipitation_mm", 0)
    wind = raw.get("wind_speed_kmh", 0)
    humid = raw.get("humidity_pct", 50)

    score = 100
    # Sıcaklık cezası
    score -= abs(temp - 20) * 2.5
    # Yağış cezası
    score -= min(rain * 8, 30)
    # Rüzgar cezası (30 km/h üzeri)
    score -= max(0, (wind - 30) * 0.6)
    # Nem aşırılığı
    if humid > 80: score -= (humid - 80) * 0.4
    if humid < 20: score -= (20 - humid) * 0.3

    return int(max(0, min(100, score)))


def ml_predict(raw: dict) -> WeatherDecision:
    """
    Ham hava verisi sözlüğünü alır, 3 ML modeli çalıştırır,
    WeatherDecision döner.
    """
    X = _encode_input(raw)

    # Model 1: Şemsiye
    u_model = _load("umbrella_model.pkl")
    u_pred = int(u_model.predict(X)[0])
    u_prob = float(u_model.predict_proba(X)[0][1])

    # Model 2: Kıyafet
    c_model = _load("clothing_model.pkl")
    c_le = _load("clothing_label_encoder.pkl")
    c_pred = int(c_model.predict(X)[0])
    c_label = c_le.inverse_transform([c_pred])[0]

    # Model 3: Aktivite uygunluğu
    s_model = _load("suitability_model.pkl")
    s_pred = int(s_model.predict(X)[0])
    s_prob = float(s_model.predict_proba(X)[0][1])

    return WeatherDecision(
        umbrella_needed=bool(u_pred),
        umbrella_prob=round(u_prob, 2),
        clothing=c_label,
        clothing_en=CLOTHING_EN.get(c_label, c_label),
        go_outside=bool(s_pred),
        go_prob=round(s_prob, 2),
        comfort_score=_comfort_score(raw),
    )


def build_prompt(raw: dict, d: WeatherDecision, time_of_day: str = "daytime") -> str:
    """
    Generates a strict English prompt for the LLM based on ML decisions.
    Enforces English output to prevent the model from responding in Turkish.
    """
    umbrella_text = "Required" if d.umbrella_needed else "Not needed"
    go_text = "Highly recommended" if d.go_outside else "Not recommended"

    # Not: Prompt içinde "Görevin:" gibi Türkçe ifadeler kalmış olabilir,
    # onları tamamen temizleyip aşağıdaki gibi İngilizceye çeviriyoruz.

    return f"""You are a Weather Intelligence Assistant. The user is planning to go out for their {time_of_day}.

### STRICT RULE: YOUR RESPONSE MUST BE ENTIRELY IN ENGLISH. ###

Weather Context:
- Temperature: {raw.get('temperature_c')}°C (Feels like: {raw.get('feels_like_c')}°C)
- Humidity: {raw.get('humidity_pct')}%
- Wind Speed: {raw.get('wind_speed_kmh')} km/h
- Current Condition: {raw.get('weather_condition')}

ML Engine Decisions:
- Suggested Clothing: {d.clothing_en}
- Umbrella Requirement: {umbrella_text}
- Outdoor Activity: {go_text}
- Environmental Comfort Score: {d.comfort_score}/100

Instruction:
Provide 2-3 short, friendly, and professional sentences of advice.
- DO NOT list the raw data (numbers).
- Use the ML decisions to form a helpful recommendation.
- Speak directly to the user in a natural tone.
- ENSURE THE ENTIRE RESPONSE IS IN ENGLISH."""


# ─── CLI TEST ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_input = {
        "temperature_c": 8,
        "feels_like_c": 4,
        "humidity_pct": 80,
        "wind_speed_kmh": 25,
        "precipitation_mm": 3.0,
        "cloud_cover_pct": 85,
        "uv_index": 1,
        "month": 4,
        "hour_of_day": 8,
        "day_of_week": 1,
        "is_weekend": 0,
        "season": "spring",
        "weather_condition": "drizzle",
    }

    print("Girdi:", test_input)
    decision = ml_predict(test_input)
    print("\nML Kararı:")
    print(f"  Şemsiye  : {'✓ Gerekli' if decision.umbrella_needed else '✗ Gerekmez'} ({decision.umbrella_prob:.0%})")
    print(f"  Kıyafet  : {decision.clothing_en}")
    print(f"  Dışarı   : {'✓ Çıkılabilir' if decision.go_outside else '✗ Tavsiye edilmez'} ({decision.go_prob:.0%})")
    print(f"  Konfor   : {decision.comfort_score}/100")

    print("\nLLM Prompt:")
    print(build_prompt(test_input, decision, "sabah çıkışı"))