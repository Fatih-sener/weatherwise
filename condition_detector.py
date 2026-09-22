import os
import numpy as np
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

_cache = {}


def _load(name):
    if name not in _cache:
        _cache[name] = joblib.load(os.path.join(MODEL_DIR, name))
    return _cache[name]


# Dashboard'da görünen açıklamalar artık İngilizce
CONDITION_ICONS = {
    "clear": ("☀️", "Clear Sky"),
    "sunny": ("☀️", "Sunny"),
    "partly_cloudy": ("⛅", "Partly Cloudy"),
    "cloudy": ("☁️", "Cloudy"),
    "overcast": ("☁️", "Overcast"),
    "fog": ("🌫️", "Foggy"),
    "drizzle": ("🌦️", "Drizzle"),
    "rain": ("🌧️", "Rainy"),
    "heavy_rain": ("🌧️", "Heavy Rain"),
    "thunderstorm": ("⛈️", "Thunderstorm"),
    "snow": ("❄️", "Snowy"),
    "blizzard": ("🌨️", "Blizzard"),
    "hail": ("🌨️", "Hail"),
    "windy": ("💨", "Windy"),
    "sleet": ("🌨️", "Sleet"),
}

WMO_MAP = {
    0: "clear",
    1: "partly_cloudy", 2: "partly_cloudy", 3: "overcast",
    45: "fog", 48: "fog",
    51: "drizzle", 53: "drizzle", 55: "drizzle",
    61: "rain", 63: "rain", 65: "heavy_rain",
    71: "snow", 73: "snow", 75: "blizzard",
    77: "snow",
    80: "rain", 81: "rain", 82: "heavy_rain",
    85: "snow", 86: "blizzard",
    95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm",
}


def condition_from_code(weather_code: int, temp: float = 15, elevation: float = 0) -> str:
    """WMO kodundan ve rakımdan dinamik kar eşiği ile hava durumu döner."""
    kar_esigi = 2 + (elevation / 500)

    if weather_code in [61, 63, 65, 80, 81, 82]:
        return "snow" if temp <= kar_esigi else "rain"  # Drizzle yerine rain daha genel durabilir

    return WMO_MAP.get(weather_code, "partly_cloudy")


def smart_condition(weather_code: int, sensor_data: dict) -> str:
    try:
        model = _load("condition_model.pkl")
        le = _load("condition_label_encoder.pkl")
        features = _load("condition_features.pkl")

        row = [sensor_data.get(f, 0) for f in features]
        X = np.array(row).reshape(1, -1)
        pred = model.predict(X)[0]
        return le.inverse_transform([pred])[0]
    except Exception:
        temp = sensor_data.get("temperature_c", 15)
        precip = sensor_data.get("precipitation_mm", 0)
        elevation = sensor_data.get("elevation", 0)
        kar_esigi = 2 + (elevation / 500)

        if precip > 0 and temp <= kar_esigi:
            return "snow"

        return condition_from_code(weather_code, temp, elevation)


def condition_to_icon_desc(condition: str):
    # Varsayılan değer de İngilizceye çevrildi
    return CONDITION_ICONS.get(condition, ("🌤️", "Partly Cloudy"))