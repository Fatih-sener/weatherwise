import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from condition_detector import smart_condition, condition_to_icon_desc, condition_from_code
import datetime
import requests
import json


def get_full_dashboard_data(city):
    try:
        # Geocoding API - Set to English for global compatibility
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url).json()
        if "results" not in geo_resp: return None

        res = geo_resp["results"][0]
        lat, lon = res["latitude"], res["longitude"]
        elevation = res.get("elevation", 0)

        # Weather API - Fetching current and forecast data
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,surface_pressure,visibility,precipitation,cloud_cover,apparent_temperature&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=weather_code,temperature_2m_max,sunrise,sunset,precipitation_probability_max&timezone=auto&forecast_days=7"
        w_data = requests.get(url).json()

        # Air Quality API
        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
        aqi_data = requests.get(aqi_url).json()

        c = w_data["current"]
        d = w_data["daily"]
        a = aqi_data["current"]

        # Mapping sensor data for the Decision Engine (Inference Layer)
        sensor_data = {
            "temperature_c": round(c["temperature_2m"], 1),
            "humidity_pct": c["relative_humidity_2m"],
            "precipitation_mm": c["precipitation"],
            "cloud_cover_pct": c.get("cloud_cover", 0),
            "visibility_km": round(c["visibility"] / 1000, 1),
            "pressure_hpa": round(c["surface_pressure"]),
            "wind_speed_kmh": round(c["wind_speed_10m"], 1),
            "elevation": elevation
        }

        # --- CONDITION LOGIC (ML & Elevation Aware) ---
        condition = smart_condition(c["weather_code"], sensor_data)
        icon, desc = condition_to_icon_desc(condition)  # Returns English from updated CONDITION_ICONS

        # Weekly Forecast Logic
        weekly_conditions = [condition_from_code(code, d["temperature_2m_max"][i], elevation) for i, code in
                             enumerate(d["weather_code"])]

        # --- ENGLISH UI DATA PREPARATION ---
        days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_days = [days_map[datetime.datetime.strptime(date, "%Y-%m-%d").weekday()] for date in d["time"]]
        weekly_icons = [condition_to_icon_desc(cond)[0] for cond in weekly_conditions]

        # AQI English Mapping
        aqi_val = a["european_aqi"]
        if aqi_val < 50:
            aqi_desc, aqi_color = "Good", "#1D9E75"
        elif aqi_val < 100:
            aqi_desc, aqi_color = "Moderate", "#EF9F27"
        else:
            aqi_desc, aqi_color = "Poor", "#E24B4A"

        # --- INTELLIGENCE ASSISTANT (English Engine) ---
        temp = c["temperature_2m"]
        precip_prob = d["precipitation_probability_max"][0]

        # Clothing Logic
        if temp < 8:
            wear_en = "Heavy Winter Coat"
        elif temp < 15:
            wear_en = "Warm Jacket / Layers"
        elif temp < 20:
            wear_en = "Light Jacket / Sweater"
        else:
            wear_en = "T-Shirt / Light Clothing"

        # Umbrella Logic
        is_raining = any(kw in condition.lower() for kw in ["rain", "snow", "drizzle", "thunderstorm", "sleet"])
        umbrella_en = "Required" if (precip_prob > 60 or is_raining) else "Not needed"

        # Final Recommendation Sentence
        if is_raining:
            reco_en = f"It's {desc.lower()} now. Please take your umbrella and stay dry."
        elif temp < 10:
            reco_en = "Cold weather alert! Make sure to wear thick layers and stay warm."
        elif temp > 28:
            reco_en = "It's quite hot today. Stay hydrated and prefer light colors."
        else:
            reco_en = "Perfect weather for outdoor activities. Enjoy your day!"

        return {
            "city": city,
            "temp": round(c["temperature_2m"], 1),
            "feels_like": round(c.get("apparent_temperature", c["temperature_2m"]), 1),
            "desc": desc,  # English text like "Cloudy" or "Rainy"
            "icon": icon,
            "condition": condition,
            "weekly_conditions": weekly_conditions,
            "hum": c["relative_humidity_2m"],
            "cloud_cover": c.get("cloud_cover", 0),
            "wind": round(c["wind_speed_10m"], 1),
            "vis": round(c["visibility"] / 1000, 1),
            "press": round(c["surface_pressure"]),
            "sunrise": d["sunrise"][0].split("T")[1],
            "sunset": d["sunset"][0].split("T")[1],
            "weekly_days": weekly_days,
            "weekly_icons": weekly_icons,
            "weekly_temps": [round(t) for t in d["temperature_2m_max"]],
            "rain_probs": d["precipitation_probability_max"],
            "chart_labels": [t.split("T")[1] for t in w_data["hourly"]["time"]],
            "chart_temps": w_data["hourly"]["temperature_2m"],
            "chart_hum": w_data["hourly"]["relative_humidity_2m"],
            "chart_wind": w_data["hourly"]["wind_speed_10m"],
            "aqi_val": round(aqi_val),
            "aqi_desc": aqi_desc,
            "aqi_color": aqi_color,
            "pm10": round(a["pm10"]),
            "o3": round(a["ozone"]),
            "so2": round(a["sulphur_dioxide"]),
            "pm25": round(a["pm2_5"]),
            "co": round(a["carbon_monoxide"]),
            "no2": round(a["nitrogen_dioxide"]),
            # English fields for the new UI components
            "wear_en": wear_en,
            "umbrella_en": umbrella_en,
            "reco_en": reco_en
        }
    except Exception as e:
        print(f"Logic Error: {e}")
        return None