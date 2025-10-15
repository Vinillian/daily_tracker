# app.py должен содержать:
import streamlit as st
from pages import diary_tab, projects_tab

st.set_page_config(page_title="📅 Ежедневный трекер + 🚀 Проекты", layout="wide")
st.title("📅 Ежедневный трекер + 🚀 Проекты")

tab1, tab2 = st.tabs(["📅 Ежедневник", "🚀 Проекты"])

with tab1:
    diary_tab.show_diary_tab()  # ← ВОТ ЭТОТ ВЫЗОВ

with tab2:
    projects_tab.show_projects_tab()