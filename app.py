import streamlit as st
import requests
from data_module.weather_api import get_full_dashboard_data
from ui_module.components import render_html_dashboard
from ui_module.style_helper import inject_dynamic_background


def get_auto_location():
    """Detects user city via IP for a personalized start."""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return response.get('city', "Sivas")
    except:
        return "Sivas"


def main():
    # --- Page Configuration ---
    st.set_page_config(page_title="WeatherWise Pro AI", page_icon="🌤️", layout="wide")

    # --- Session Initialization ---
    if 'initialized' not in st.session_state:
        st.session_state.current_city = get_auto_location()
        st.session_state.condition = "clear"
        st.session_state.initialized = True

    # Inject Background Style
    inject_dynamic_background(st.session_state.condition)

    # City List (English labels)
    cities = ["Sivas", "Erzincan", "Istanbul", "Ankara", "Izmir", "Antalya", "Erzurum", "Trabzon", "London", "New York",
              "Tokyo"]

    # Handle index for selectbox
    try:
        current_index = cities.index(st.session_state.current_city)
    except ValueError:
        current_index = 0

    # --- Header & Input ---
    st.title("WeatherWise AI Assistant")
    selected_city = st.selectbox("🌍 Select City for Analysis:", cities, index=current_index)

    # --- Loading & Analysis ---
    with st.spinner("Synchronizing satellite data and ML models..."):
        dashboard_data = get_full_dashboard_data(selected_city)

        if dashboard_data:
            # Update background based on current condition
            st.session_state.condition = dashboard_data["condition"]
            inject_dynamic_background(dashboard_data["condition"])

            # Render HTML Dashboard
            render_html_dashboard(dashboard_data)

            st.markdown("---")
            st.subheader("🤖 WeatherWise Intelligence Assistant")

            # --- ML DECISION & LLM RECOMMENDATION BLOCK ---
            try:
                # Backend URL (Flask ML Server)
                flask_url = 'http://127.0.0.1:5000/get_prompt'

                # Posting weather data to ML Backend
                api_response = requests.post(flask_url, json={'weather': dashboard_data}, timeout=10)

                if api_response.status_code == 200:
                    ml_result = api_response.json()

                    # --- GÜVENLİK AĞI: TÜRKÇE ÇIKTILARI YAKALA VE ÇEVİR ---
                    TR_TO_EN_CLOTHING = {
                        "Çok ince giysiler, bol su": "Very light clothing",
                        "Tişört, rahat giyim": "T-shirt and comfortable pants",
                        "İnce, nefes alan giysiler": "Light, breathable clothing",
                        "İnce ceket veya kazak": "Light jacket or sweater",
                        "Uzun kollu, hafif katman": "Long sleeves or a light layer",
                        "Katmanlı giyim, mont": "Warm jacket and layers",
                        "Kışlık mont, atkı, eldiven": "Winter coat, scarf, and gloves",
                        "Kalın kışlık mont, bere, eldiven": "Heavy winter coat, gloves, and a hat"
                    }

                    # Flask'tan gelen raw (ham) string'i al
                    raw_wear = ml_result.get('clothing', 'Undetermined')

                    # Eğer sözlükte varsa İngilizcesini al, yoksa Flask'tan geleni olduğu gibi kullan
                    english_wear = TR_TO_EN_CLOTHING.get(raw_wear, raw_wear)

                    # Dashboard Metrics
                    c1, c2, c3 = st.columns(3)
                    c1.metric("🧥 Suggested Wear", english_wear)
                    c2.metric("☂️ Umbrella Status", "Required" if ml_result.get('umbrella') else "Not needed")
                    c3.metric("🌿 Comfort Score", f"{ml_result.get('comfort_score', 0)}/100")

                    # LLM Insight Text
                    if 'llm_text' in ml_result:
                        st.info(f"💬 **Assistant Insight:** {ml_result['llm_text']}")

                    # Activity Approval
                    if ml_result.get('go_outside'):
                        st.success("✅ According to our algorithms, weather is suitable for outdoor activities!")
                    else:
                        st.warning("⚠️ Conditions might be challenging. We recommend staying cautious.")

                else:
                    st.warning("⚠️ ML Service reached, but returned an error state.")
            except Exception as e:
                # In Hackathon, clear instructions help the jury
                st.error("🔌 ML Backend (Flask) is offline. Please ensure the backend server is running.")
        else:
            st.error("❌ Data retrieval failed. Please check your internet connection or API keys.")


if __name__ == "__main__":
    main()