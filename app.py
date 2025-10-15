import streamlit as st
from ui.diary_tab import diary_tab
from ui.projects_tab import projects_tab


def main():
    """Главная функция приложения"""
    st.set_page_config(
        page_title="📅 Ежедневный трекер + 🚀 Проекты",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📅 Ежедневный трекер + 🚀 Проекты")

    # Создаем вкладки
    tab1, tab2 = st.tabs(["📅 Ежедневник", "🚀 Проекты"])

    with tab1:
        diary_tab.show_diary_tab()

    with tab2:
        projects_tab.show_projects_tab()


if __name__ == "__main__":
    main()