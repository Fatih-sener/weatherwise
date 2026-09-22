import os
import sys
import json
import urllib.request
from datetime import datetime
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.dirname(__file__))
from inference import ml_predict, build_prompt

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

CONDITION_MAP = {
    "rain": "drizzle", "heavy_rain": "drizzle", "drizzle": "drizzle",
    "snow": "snow", "sun": "clear", "clear": "clear",
    "cloud": "cloudy", "cloudy": "cloudy", "partly_cloudy": "partly_cloudy",
    "thunderstorm": "thunderstorm", "hail": "hail", "fog": "cloudy",
}


def guess_season(month):
    if month in (12, 1, 2): return "winter"
    if month in (3, 4, 5):  return "spring"
    if month in (6, 7, 8):  return "summer"
    return "autumn"


def dashboard_to_ml_input(d):
    now = datetime.now()
    dow = now.weekday()
    condition_ml = CONDITION_MAP.get(d.get("condition", "clear"), "cloudy")
    precip = d.get("precip", 0)
    rain_probs = d.get("rain_probs", [0])
    if (rain_probs[0] if rain_probs else 0) >= 60 and precip < 0.5:
        precip = 2.0
    return {
        "temperature_c": d.get("temp", 15),
        "feels_like_c": d.get("feels_like", d.get("temp", 15)),
        "humidity_pct": d.get("hum", 50),
        "wind_speed_kmh": d.get("wind", 0),
        "precipitation_mm": precip,
        "cloud_cover_pct": d.get("cloud_cover", 0),
        "uv_index": d.get("uv_index", 2),
        "month": now.month,
        "hour_of_day": now.hour,
        "day_of_week": dow,
        "is_weekend": 1 if dow >= 5 else 0,
        "season": guess_season(now.month),
        "weather_condition": condition_ml,
    }


def call_claude(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        return "API anahtarı tanımlı değil. Lütfen ANTHROPIC_API_KEY ortam değişkenini set edin."

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        return data["content"][0]["text"]


@app.route("/get_prompt", methods=["POST"])
def get_prompt():
    try:
        body = request.get_json(force=True)
        dashboard = body.get("weather", {})
        time_of_day = body.get("time_of_day", "gün içi")

        ml_input = dashboard_to_ml_input(dashboard)
        decision = ml_predict(ml_input)
        prompt = build_prompt(ml_input, decision, time_of_day)

        try:
            llm_text = call_claude(prompt)
        except Exception as e:
            llm_text = f"LLM yanıtı alınamadı: {e}"

        return jsonify({
            "prompt": prompt,
            "llm_text": llm_text,
            "umbrella": int(decision.umbrella_needed),
            "umbrella_prob": decision.umbrella_prob,
            "clothing": decision.clothing_en,
            "go_outside": int(decision.go_outside),
            "comfort_score": decision.comfort_score,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("Flask ML servisi başlatılıyor → http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
