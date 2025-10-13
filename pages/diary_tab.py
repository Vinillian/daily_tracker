import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from utils.file_utils import load_json, save_json, copy_template, ensure_dir

DATA_DIR = Path("data")
DIARY_DIR = DATA_DIR / "diary"
TEMPLATE_DIR = Path("templates/daily_templates")

# Создаем директории, если их нет
ensure_dir(DIARY_DIR)

def show_diary_tab():
    all_days = sorted([f.stem for f in DIARY_DIR.glob("*.json")], reverse=True)
    selected_day = st.selectbox("Выберите день для просмотра", all_days)

    # Создание завтрашнего дня
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_file = DIARY_DIR / f"{tomorrow}.json"

    daily_template_files = sorted(TEMPLATE_DIR.glob("*.json"))
    daily_template_names = [f.stem for f in daily_template_files]
    selected_daily_template = st.selectbox("Шаблон для завтрашнего дня", daily_template_names)

    if st.button("Создать пустой завтрашний день"):
        empty_template = {"Утро": [], "День": [], "Вечер": []}
        save_json(tomorrow_file, empty_template)
        st.success(f"Пустой день на {tomorrow} создан!")

    if st.button("Создать завтрашний день из шаблона"):
        template_file = TEMPLATE_DIR / f"{selected_daily_template}.json"
        copy_template(template_file, tomorrow_file)
        st.success(f"Завтрашний день на {tomorrow} создан из шаблона '{selected_daily_template}'!")

    # Просмотр и редактирование выбранного дня
    day_file = DIARY_DIR / f"{selected_day}.json"
    day_data = load_json(day_file)

    st.subheader(f"День: {selected_day}")
    for period in ["Утро", "День", "Вечер"]:
        st.markdown(f"### {period}")
        for i, task in enumerate(day_data.get(period, [])):
            cols = st.columns([4,2,2])
            cols[0].write(task["задача"])
            cols[1].write(task["время"])
            task["статус"] = cols[2].selectbox(
                "Статус",
                ["☐","✅","☑️","❌"],
                index=["☐","✅","☑️","❌"].index(task["статус"]),
                key=f"{period}_{i}_status"
            )

    save_json(day_file, day_data)
