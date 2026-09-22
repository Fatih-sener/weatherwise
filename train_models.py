"""
Katman 1 — ML Karar Motoru
Üç ayrı model eğitir:
  1. umbrella_model    → şemsiye gerekli mi? (binary classification)
  2. clothing_model    → hangi kıyafet? (multi-class classification)
  3. suitability_model → dışarı çıkılır mı? (binary classification)

Kullanılan veri: activity_recommendations.csv + hourly_observations.csv
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── FEATURE COLUMNS ─────────────────────────────────────────────────────────
NUMERIC_FEATURES = [
    "temperature_c", "feels_like_c", "humidity_pct",
    "wind_speed_kmh", "precipitation_mm", "cloud_cover_pct",
    "uv_index", "month", "hour_of_day", "day_of_week", "is_weekend"
]

CATEGORICAL_FEATURES = ["season", "weather_condition"]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_and_merge() -> pd.DataFrame:
    """
    activity_recommendations.csv  →  etiketleri (umbrella, clothing, go_or_no)
    hourly_observations.csv        →  ek ham gözlem verisi
    ikisini birleştirir.
    """
    rec  = pd.read_csv(os.path.join(DATA_DIR, "activity_recommendations.csv"))
    obs  = pd.read_csv(os.path.join(DATA_DIR, "hourly_observations.csv"))

    # obs'tan sadece gerekli sütunları al, farklı olmayan etiketler için
    obs_subset = obs[[
        "temperature_c", "feels_like_c", "humidity_pct",
        "wind_speed_kmh", "precipitation_mm", "cloud_cover_pct",
        "uv_index", "month", "hour_of_day", "day_of_week", "is_weekend",
        "season", "weather_condition",
        "umbrella_needed", "clothing_recommendation",
        "outdoor_suitability_score"
    ]].copy()
    obs_subset["go_or_no"] = (obs_subset["outdoor_suitability_score"] >= 5).astype(int)
    obs_subset = obs_subset.drop(columns=["outdoor_suitability_score"])

    rec_subset = rec[[
        "temperature_c", "feels_like_c", "humidity_pct",
        "wind_speed_kmh", "precipitation_mm", "cloud_cover_pct",
        "uv_index", "month", "hour_of_day", "day_of_week", "is_weekend",
        "season", "weather_condition",
        "umbrella_needed", "clothing_recommendation", "go_or_no"
    ]].copy()

    combined = pd.concat([rec_subset, obs_subset], ignore_index=True)
    combined = combined.dropna(subset=ALL_FEATURES)
    print(f"[veri] toplam satır: {len(combined):,}")
    return combined


def encode_categoricals(df: pd.DataFrame):
    """Kategorik sütunları sayıya çevirir, encoder'ları kaydeder."""
    encoders = {}
    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    joblib.dump(encoders, os.path.join(MODEL_DIR, "label_encoders.pkl"))
    print("[encode] kategorik encoder'lar kaydedildi.")
    return df, encoders


def train_umbrella_model(X_train, X_test, y_train, y_test):
    """XGBoost ile şemsiye modeli — binary classification."""
    print("\n[model 1] şemsiye modeli eğitiliyor...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"  doğruluk: {acc:.3f}")
    print(classification_report(y_test, preds, target_names=["gerekmez", "gerekli"]))
    joblib.dump(model, os.path.join(MODEL_DIR, "umbrella_model.pkl"))
    print("  → models/umbrella_model.pkl kaydedildi")
    return model


def train_clothing_model(X_train, X_test, y_train, y_test, label_names):
    """Random Forest ile kıyafet modeli — multi-class classification."""
    print("\n[model 2] kıyafet modeli eğitiliyor...")
    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"  doğruluk: {acc:.3f}")
    print(classification_report(y_test, preds, labels=list(range(len(label_names))), target_names=label_names, zero_division=0))
    joblib.dump(model, os.path.join(MODEL_DIR, "clothing_model.pkl"))
    print("  → models/clothing_model.pkl kaydedildi")
    return model


def train_suitability_model(X_train, X_test, y_train, y_test):
    """GradientBoosting ile aktivite uygunluğu — binary classification."""
    print("\n[model 3] aktivite uygunluk modeli eğitiliyor...")
    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        random_state=42
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"  doğruluk: {acc:.3f}")
    print(classification_report(y_test, preds, target_names=["çıkma", "çık"]))
    joblib.dump(model, os.path.join(MODEL_DIR, "suitability_model.pkl"))
    print("  → models/suitability_model.pkl kaydedildi")
    return model


def main():
    print("=" * 60)
    print("WeatherWise — Model Eğitimi")
    print("=" * 60)

    # 1. Veriyi yükle ve birleştir
    df = load_and_merge()

    # 2. Kıyafet etiketini encode et
    clothing_le = LabelEncoder()
    df["clothing_encoded"] = clothing_le.fit_transform(df["clothing_recommendation"].astype(str))
    joblib.dump(clothing_le, os.path.join(MODEL_DIR, "clothing_label_encoder.pkl"))
    print(f"[encode] kıyafet sınıfları: {list(clothing_le.classes_)}")

    # 3. Kategorik feature'ları encode et
    df, _ = encode_categoricals(df)

    X = df[ALL_FEATURES].values
    y_umbrella    = df["umbrella_needed"].values.astype(int)
    y_clothing    = df["clothing_encoded"].values.astype(int)
    y_suitability = df["go_or_no"].values.astype(int)

    # 4. Train/test split
    X_tr, X_te, yu_tr, yu_te, yc_tr, yc_te, ys_tr, ys_te = train_test_split(
        X, y_umbrella, y_clothing, y_suitability,
        test_size=0.2, random_state=42, stratify=y_umbrella
    )
    print(f"\n[split] eğitim: {len(X_tr):,} | test: {len(X_te):,}")

    # 5. Modelleri eğit
    train_umbrella_model(X_tr, X_te, yu_tr, yu_te)
    train_clothing_model(X_tr, X_te, yc_tr, yc_te, list(clothing_le.classes_))
    train_suitability_model(X_tr, X_te, ys_tr, ys_te)

    # 6. Feature isimlerini kaydet (inference için lazım)
    joblib.dump(ALL_FEATURES, os.path.join(MODEL_DIR, "feature_names.pkl"))

    print("\n[bitti] tüm modeller models/ klasörüne kaydedildi.")
    print("Sonraki adım: python inference.py ile test et")


if __name__ == "__main__":
    main()