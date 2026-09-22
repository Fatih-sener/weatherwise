"""
Layer 3 — LLM (Claude API) Natural Language Generation

get_recommendation(raw_weather, time_of_day, api_key) -> str

Pipeline:
  raw_weather dict
      ↓  [Layer 1] ml_predict()
  WeatherDecision
      ↓  [Layer 2] build_prompt()
  Prompt string
      ↓  [Layer 3] Claude API
  Natural Language Recommendation
"""

import os
import json
import urllib.request
import urllib.error
from inference import ml_predict, build_prompt, WeatherDecision


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL             = "claude-sonnet-4-20250514"


def call_claude(prompt: str, api_key: str, max_tokens: int = 300) -> str:
    """
    This function is deprecated in the local script.
    The API call is now handled by the frontend/Flask bridge.
    See: /get_prompt endpoint in app.py.
    """
    raise NotImplementedError("API calls must be handled through the frontend/backend bridge.")

def get_recommendation(
    raw_weather: dict,
    time_of_day: str = "daytime",
    api_key: str | None = None,
) -> dict:
    """
    Executes the full pipeline.

    Returns:
    {
        "ml_decision": WeatherDecision,
        "prompt":      str,
        "llm_text":    str,
    }

    If api_key is None, it reads from ANTHROPIC_API_KEY environment variable.
    """
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError(
            "API Key not found. "
            "Set the ANTHROPIC_API_KEY env var or pass the api_key parameter."
        )

    # Layer 1: ML Decision
    decision = ml_predict(raw_weather)

    # Layer 2: Build Prompt
    prompt = build_prompt(raw_weather, decision, time_of_day)

    # Layer 3: LLM Text Generation
    llm_text = call_claude(prompt, api_key)

    return {
        "ml_decision": decision,
        "prompt":      prompt,
        "llm_text":    llm_text,
    }


# ─── CLI TEST ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("  Run: export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    # Test input — realistic scenario
    weather = {
        "temperature_c":     12,
        "feels_like_c":      8,
        "humidity_pct":      85,
        "wind_speed_kmh":    30,
        "precipitation_mm":  5.2,
        "cloud_cover_pct":   90,
        "uv_index":          1,
        "month":             11,
        "hour_of_day":       7,
        "day_of_week":       0,
        "is_weekend":        0,
        "season":            "autumn",
        "weather_condition": "drizzle",
    }

    print("Pipeline executing...\n")
    result = get_recommendation(weather, time_of_day="morning commute", api_key=api_key)

    d = result["ml_decision"]
    print("─" * 50)
    print("LAYER 1 — ML Decision")
    print(f"  Umbrella  : {'✓ Required' if d.umbrella_needed else '✗ Not Needed'} ({d.umbrella_prob:.0%})")
    print(f"  Clothing  : {d.clothing_en}")
    print(f"  Outdoors  : {'✓ Suitable' if d.go_outside else '✗ Not Recommended'} ({d.go_prob:.0%})")
    print(f"  Comfort   : {d.comfort_score}/100")
    print()
    print("─" * 50)
    print("LAYER 3 — Claude Response")
    print(result["llm_text"])
    print("─" * 50)