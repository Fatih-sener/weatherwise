import pandas as pd
import numpy as np
import joblib
import os
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURES = [
    "temperature_c", "dew_point_c", "humidity_pct",
    "pressure_hpa", "wind_speed_kmh", "wind_gust_kmh",
    "precipitation_mm", "cloud_cover_pct", "visibility_km"
]

def main():
    print("=" * 50)
    print("Hava Koşulu Modeli Eğitimi")
    print("=" * 50)

    df = pd.read_csv(os.path.join(DATA_DIR, "hourly_observations.csv"))
    df = df.dropna(subset=FEATURES + ["weather_condition"])
    print(f"Veri: {len(df):,} satır")
    print(df["weather_condition"].value_counts().to_string())

    le = LabelEncoder()
    y  = le.fit_transform(df["weather_condition"])
    X  = df[FEATURES].values

    # 1'den az örneği olan sınıfları filtrele
    counts = Counter(y)
    mask = np.array([counts[label] >= 2 for label in y])
    X, y = X[mask], y[mask]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_tr, y_tr)

    preds = model.predict(X_te)
    print(f"\nDoğruluk: {accuracy_score(y_te, preds):.3f}")
    print(classification_report(y_te, preds, labels=list(range(len(le.classes_))), target_names=list(le.classes_), zero_division=0))

    joblib.dump(model, os.path.join(MODEL_DIR, "condition_model.pkl"))
    joblib.dump(le,    os.path.join(MODEL_DIR, "condition_label_encoder.pkl"))
    joblib.dump(FEATURES, os.path.join(MODEL_DIR, "condition_features.pkl"))

    print("\n→ models/condition_model.pkl kaydedildi")

if __name__ == "__main__":
    main()