import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from utils.file_utils import load_json, save_json, copy_template, ensure_dir

DATA_DIR = Path("data")
DIARY_DIR = DATA_DIR / "diary"
TEMPLATE_DIR = Path("templates/daily_templates")

# Создаем директории, если их нет
ensure_dir(DIARY_DIR)


def progress_bar(percent: int):
    """Создает текстовый прогресс-бар"""
    filled = "█" * (percent // 10)
    empty = "░" * (10 - percent // 10)
    return f"{filled}{empty} {percent}%"


def calc_category_progress(data, keywords):
    """Вычисляет прогресс по категориям"""
    values = []
    for period in data.values():
        for task in period:
            if any(word.lower() in task['задача'].lower() for word in keywords):
                values.append(task['прогресс'])
    return round(sum(values) / len(values)) if values else 0


def show_diary_tab():
    # Боковая панель - управление днями
    st.sidebar.header("📅 Управление днями")

    # Создание нового дня
    st.sidebar.subheader("Создать новый день")

    tomorrow = date.today() + timedelta(days=1)
    tomorrow_file = DIARY_DIR / f"{tomorrow}.json"

    daily_template_files = sorted(TEMPLATE_DIR.glob("*.json"))
    daily_template_names = [f.stem for f in daily_template_files]

    creation_type = st.sidebar.radio(
        "Тип дня:",
        ["📝 Пустой день", "🎯 Из шаблона"],
        key="day_creation_type"
    )

    if creation_type == "🎯 Из шаблона":
        selected_daily_template = st.sidebar.selectbox(
            "Шаблон дня",
            daily_template_names,
            key="daily_template"
        )

        if st.sidebar.button("📅 Создать завтра из шаблона", use_container_width=True):
            template_file = TEMPLATE_DIR / f"{selected_daily_template}.json"
            copy_template(template_file, tomorrow_file)
            st.sidebar.success(f"Завтрашний день на {tomorrow} создан из шаблона '{selected_daily_template}'!")
            st.rerun()

    else:  # Пустой день
        if st.sidebar.button("📄 Создать пустой завтрашний день", use_container_width=True):
            empty_template = {"Утро": [], "День": [], "Вечер": []}
            save_json(tomorrow_file, empty_template)
            st.sidebar.success(f"Пустой день на {tomorrow} создан!")
            st.rerun()

    # Добавление новой задачи
    st.sidebar.subheader("➕ Добавить задачу")
    period_select = st.sidebar.selectbox("Период", ["Утро", "День", "Вечер"], key="new_task_period")
    task_name = st.sidebar.text_input("Название задачи", key="new_task_name")
    task_time = st.sidebar.text_input("Время (например 7:30–8:00)", key="new_task_time")

    if st.sidebar.button("Добавить задачу", use_container_width=True) and task_name:
        # Загружаем текущий день чтобы добавить задачу
        all_days = sorted([f.stem for f in DIARY_DIR.glob("*.json")], reverse=True)
        if all_days:
            selected_day = all_days[0]  # Берем последний день
            day_file = DIARY_DIR / f"{selected_day}.json"
            day_data = load_json(day_file)

            if period_select not in day_data:
                day_data[period_select] = []

            day_data[period_select].append({
                "задача": task_name,
                "время": task_time,
                "статус": "☐",
                "прогресс": 0
            })
            save_json(day_file, day_data)
            st.sidebar.success("Задача добавлена!")
            st.rerun()

    # Выбор дня для просмотра
    st.sidebar.subheader("Просмотр дней")
    all_days = sorted([f.stem for f in DIARY_DIR.glob("*.json")], reverse=True)

    if not all_days:
        st.sidebar.info("📝 Дней пока нет. Создайте первый день!")
        selected_day = None
    else:
        selected_day = st.sidebar.selectbox(
            "Выберите день",
            all_days,
            key="day_selection"
        )

    # Основная область - работа с выбранным днем
    if selected_day:
        day_file = DIARY_DIR / f"{selected_day}.json"
        day_data = load_json(day_file)

        st.header(f"📅 День: {selected_day}")

        # Периоды дня с иконками
        period_icons = {"Утро": "🌅", "День": "🌞", "Вечер": "🌇"}

        for period in ["Утро", "День", "Вечер"]:
            if period in day_data and day_data[period]:
                st.subheader(f"{period_icons[period]} {period} ({len(day_data[period])} задач)")

                # Отображение задач с редактированием
                for i, task in enumerate(day_data[period]):
                    cols = st.columns([4, 2, 2, 2, 1])

                    # Название задачи
                    with cols[0]:
                        new_task = st.text_input(
                            "Задача",
                            value=task["задача"],
                            key=f"{selected_day}_{period}_{i}_task"
                        )
                        task["задача"] = new_task

                    # Время
                    with cols[1]:
                        new_time = st.text_input(
                            "Время",
                            value=task["время"],
                            key=f"{selected_day}_{period}_{i}_time"
                        )
                        task["время"] = new_time

                    # Статус
                    with cols[2]:
                        task["статус"] = st.selectbox(
                            "Статус",
                            ["☐", "✅", "☑️", "❌"],
                            index=["☐", "✅", "☑️", "❌"].index(task["статус"]),
                            key=f"{selected_day}_{period}_{i}_status"
                        )

                    # Прогресс с ползунком
                    with cols[3]:
                        task["прогресс"] = st.slider(
                            "Прогресс",
                            0, 100,
                            task["прогресс"],
                            key=f"{selected_day}_{period}_{i}_progress"
                        )

                    # Кнопка удаления
                    with cols[4]:
                        if st.button("❌", key=f"{selected_day}_{period}_{i}_delete"):
                            day_data[period].pop(i)
                            save_json(day_file, day_data)
                            st.rerun()

                st.markdown("---")

        # Автосохранение при изменениях
        save_json(day_file, day_data)

        # 📊 Общий статус дня
        st.header("📊 Общий статус дня")

        categories = {
            "💻 Разработка (Hive/UI)": ["код", "работа", "dev", "flutter", "android", "hive", "ui", "дизайн"],
            "🧘 Энергетические практики": ["медитация", "тайцзи", "ци-гун", "мантра", "дыхание"],
            "🧠 Изучение / чтение": ["чтение", "изучение", "шб", "дао", "книга"],
            "🍽 Быт и восстановление": ["обед", "ужин", "завтрак", "отдых", "сон", "быт"]
        }

        summary_md = "| Поток | Прогресс | Оценка |\n|-------|:---------:|:------:|\n"

        for cat, keywords in categories.items():
            avg = calc_category_progress(day_data, keywords)
            status = "⚙️ В процессе" if avg < 100 else "✅ Завершено"
            summary_md += f"| {cat} | {progress_bar(avg)} | {status} |\n"

        st.markdown(summary_md)

    else:
        # Экран при отсутствии дней
        if not all_days:
            st.info("""
            ## 📅 Добро пожаловать в ежедневник!

            Здесь вы можете:
            - 📝 **Создавать расписания** на день
            - 🎯 **Использовать шаблоны** для разных типов дней
            - ✅ **Отслеживать выполнение** задач с прогресс-барами
            - ⏰ **Планировать время** по периодам дня
            - 📊 **Видеть статистику** по категориям задач

            **Чтобы начать, создайте ваш первый день в боковой панели!**
            """)
        else:
            st.info("👈 Выберите день для просмотра в боковой панели")