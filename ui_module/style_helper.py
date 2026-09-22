import streamlit as st

def inject_dynamic_background(condition="sun"):
    # Arka plan geçişi artık tamamen JavaScript (opacity fade) ile yönetiliyor.
    # Burada sadece Streamlit'in kendi menüsünü gizliyor ve varsayılan arka planı temizliyoruz.
    st.markdown("""
        <style>
        .stApp {
            background: transparent !important;
            background-color: #0d1117 !important;
            background-image: none !important;
        }
        header { visibility: hidden; } 
        </style>
    """, unsafe_allow_html=True)