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


def get_auto_categories():
    """Возвращает автоматические категории для анализа дня"""
    return {
        "🩺 Здоровье": ["🩺", "🚑", "💊", "врач", "больниц", "здоровь", "нейрохирург", "приём", "консультация", "диагностика"],
        "💼 Работа": ["📦", "💼", "🚚", "курьер", "работ", "доход", "зарабат", "проект"],
        "📚 Обучение": ["📚", "🧮", "📖", "python", "изучение", "лекция", "чтение", "марк лутц", "класс", "атрибут", "программирование"],
        "🧘 Практики": ["🕉️", "🧘", "☯️", "медитац", "мантра", "растяжка", "даосизм", "духовн", "практик"],
        "🏠 Быт": ["🏠", "🛏️", "☕", "🍽️", "🛀", "уборк", "завтрак", "ужин", "сбор", "документ", "дом"],
        "🎭 Отдых": ["📺", "🎬", "🚶", "сериал", "отдых", "прогулка", "разговор", "хобби", "развлечен"]
    }


def get_all_categories():
    """Возвращает все доступные категории для выбора"""
    return [
        "🩺 Здоровье", "💼 Работа", "📚 Обучение",
        "🧘 Практики", "🏠 Быт", "🎭 Отдых",
        "👥 Общение", "💖 Отношения", "🌱 Развитие",
        "🎨 Творчество", "🏃 Спорт", "🙏 Духовное",
        "💰 Финансы", "🚀 Проекты", "🌍 Путешествия"
    ]


def suggest_category(task_text):
    """Автоматически предлагает категорию по тексту задачи"""
    if not task_text:
        return "🏠 Быт"

    task_lower = task_text.lower()
    auto_categories = get_auto_categories()

    for cat_name, keywords in auto_categories.items():
        if any(keyword in task_lower for keyword in keywords):
            return cat_name

    return "🏠 Быт"  # категория по умолчанию


def calc_category_progress_v2(data):
    """Новый расчет прогресса - использует явные категории задач"""
    category_progress = {}

    for period in ["Утро", "День", "Вечер"]:
        if period in data and isinstance(data[period], list):
            for task in data[period]:
                if isinstance(task, dict) and 'категория' in task and 'прогресс' in task:
                    category = task['категория']
                    if category not in category_progress:
                        category_progress[category] = []
                    category_progress[category].append(task['прогресс'])

    # Возвращаем средние значения по категориям
    return {cat: round(sum(progress) / len(progress))
            for cat, progress in category_progress.items() if progress}


def calc_category_progress(data, keywords):
    """Вычисляет прогресс по категориям с защитой от ошибок"""
    values = []

    # Стандартные периоды дня
    standard_periods = ["Утро", "День", "Вечер"]

    for period_name in standard_periods:
        if period_name in data and isinstance(data[period_name], list):
            for task in data[period_name]:
                # Проверяем, что задача имеет нужную структуру
                if isinstance(task, dict) and 'задача' in task and 'прогресс' in task:
                    task_text = task['задача'].lower()
                    if any(word.lower() in task_text for word in keywords):
                        values.append(task['прогресс'])

    return round(sum(values) / len(values)) if values else 0


def load_day_data(selected_day):
    """Загрузка данных дня с созданием если нет + миграция старых данных"""
    day_file = DIARY_DIR / f"{selected_day}.json"

    if day_file.exists():
        data = load_json(day_file)
        # Обеспечиваем наличие всех основных полей
        if "Утро" not in data:
            data["Утро"] = []
        if "День" not in data:
            data["День"] = []
        if "Вечер" not in data:
            data["Вечер"] = []
        if "Состояние" not in data:
            data["Состояние"] = {}
        if "Заметки" not in data:
            data["Заметки"] = []

        # МИГРАЦИЯ: добавляем категории к старым задачам
        for period in ["Утро", "День", "Вечер"]:
            if period in data and isinstance(data[period], list):
                for task in data[period]:
                    if "категория" not in task:
                        # Автоматически определяем категорию для старых задач
                        task["категория"] = suggest_category(task.get("задача", ""))

        return data
    else:
        # Создаем базовую структуру
        base_structure = {
            "Утро": [],
            "День": [],
            "Вечер": [],
            "Состояние": {},
            "Заметки": []
        }
        save_json(day_file, base_structure)
        return base_structure





def show_state_metrics(state_data):
    """Отображает метрики состояния и самочувствия"""
    if not state_data or not isinstance(state_data, dict):
        return

    st.header("💫 Состояние и самочувствие")

    # Основные метрики в колонках
    col1, col2, col3, col4, col5 = st.columns(5)

    metrics_config = [
        ("💪 Тело", col1),
        ("🧘 Энергия", col2),
        ("🧠 Концентрация", col3),
        ("🌿 Настроение", col4),
        ("💨 Пищеварение", col5)
    ]

    for metric_name, col in metrics_config:
        with col:
            value = state_data.get(metric_name, "0%")
            # Убираем % для числового значения если нужно
            numeric_value = value.replace('%', '') if isinstance(value, str) else value
            try:
                numeric_value = int(numeric_value)
                st.metric(metric_name, f"{numeric_value}%")
            except (ValueError, TypeError):
                st.metric(metric_name, value)

    # Дополнительные факторы
    if "🌦️ Фактор погоды" in state_data:
        st.info(f"**🌦️ Фактор:** {state_data['🌦️ Фактор погоды']}")

    if "💭 Общее состояние" in state_data:
        st.write(f"**💭 Общее:** {state_data['💭 Общее состояние']}")


def show_notes(notes_data):
    """Отображает заметки и инсайты"""
    if not notes_data or not isinstance(notes_data, list):
        return

    st.header("📝 Заметки и инсайты")

    for i, note in enumerate(notes_data):
        if note.strip():  # Показывать только непустые заметки
            st.write(f"• {note}")


def show_auto_analysis(day_data):
    """Автоматический анализ дня по категориям"""
    st.header("📊 Анализ дня по категориям")

    # Пробуем использовать явные категории из задач
    explicit_categories = calc_category_progress_v2(day_data)

    if explicit_categories:
        # Используем явные категории из задач
        summary_md = "| Категория | Прогресс | Статус |\n|-----------|:---------:|:-------:|\n"

        for cat_name, avg in sorted(explicit_categories.items(), key=lambda x: x[1], reverse=True):
            if avg >= 90:
                status = "✅ Завершено"
            elif avg >= 70:
                status = "🟢 Хорошо"
            elif avg >= 50:
                status = "🟡 В процессе"
            else:
                status = "🔴 Начато"
            summary_md += f"| {cat_name} | {progress_bar(avg)} | {status} |\n"

        st.markdown(summary_md)
        st.caption("💡 На основе выбранных категорий задач")

    else:
        # Fallback на автоматическую категоризацию по ключевым словам
        auto_categories = get_auto_categories()
        summary_md = "| Категория | Прогресс | Статус |\n|-----------|:---------:|:-------:|\n"

        active_categories = []

        for cat_name, cat_keywords in auto_categories.items():
            avg = calc_category_progress(day_data, cat_keywords)
            if avg > 0:  # Показывать только категории с активностью
                active_categories.append((cat_name, avg))

        # Сортируем по прогрессу (убывание)
        active_categories.sort(key=lambda x: x[1], reverse=True)

        for cat_name, avg in active_categories:
            if avg >= 90:
                status = "✅ Завершено"
            elif avg >= 70:
                status = "🟢 Хорошо"
            elif avg >= 50:
                status = "🟡 В процессе"
            else:
                status = "🔴 Начато"
            summary_md += f"| {cat_name} | {progress_bar(avg)} | {status} |\n"

        if active_categories:
            st.markdown(summary_md)
            st.caption("💡 На основе автоматического анализа задач")
        else:
            st.info("🤔 Недостаточно данных для анализа категорий")


def show_tasks_compact(period_name, tasks, selected_day, day_data, day_file):
    """Компактное отображение задач в expander с категориями"""
    period_icons = {"Утро": "🌅", "День": "🌞", "Вечер": "🌇"}
    icon = period_icons.get(period_name, "📝")

    with st.expander(f"{icon} {period_name} ({len(tasks)} задач)", expanded=True):
        for i, task in enumerate(tasks):
            cols = st.columns([3, 2, 2, 2, 2, 1])

            with cols[0]:
                task["задача"] = st.text_input(
                    "Задача", task["задача"],
                    key=f"{selected_day}_{period_name}_{i}_task",
                    label_visibility="collapsed",
                    placeholder="Название задачи..."
                )
            with cols[1]:
                task["время"] = st.text_input(
                    "Время", task["время"],
                    key=f"{selected_day}_{period_name}_{i}_time",
                    label_visibility="collapsed",
                    placeholder="Время..."
                )
            with cols[2]:
                # НОВОЕ: Выбор категории для существующей задачи
                current_category = task.get("категория", "🏠 Быт")
                task["категория"] = st.selectbox(
                    "Категория",
                    get_all_categories(),
                    index=get_all_categories().index(
                        current_category) if current_category in get_all_categories() else 0,
                    key=f"{selected_day}_{period_name}_{i}_category",
                    label_visibility="collapsed"
                )
            with cols[3]:
                task["статус"] = st.selectbox(
                    "Статус", ["☐", "✅", "☑️", "❌"],
                    index=["☐", "✅", "☑️", "❌"].index(task["статус"]),
                    key=f"{selected_day}_{period_name}_{i}_status",
                    label_visibility="collapsed"
                )
            with cols[4]:
                task["прогресс"] = st.slider(
                    "Прогресс", 0, 100, task["прогресс"],
                    key=f"{selected_day}_{period_name}_{i}_progress",
                    label_visibility="collapsed"
                )
            with cols[5]:
                if st.button("❌", key=f"{selected_day}_{period_name}_{i}_delete"):
                    tasks.pop(i)
                    save_json(day_file, day_data)
                    st.rerun()

        # Кнопка добавления новой задачи в этот период
        if st.button(f"➕ Добавить в {period_name}", key=f"add_{period_name}", use_container_width=True):
            tasks.append({
                "задача": "Новая задача",
                "время": "",
                "статус": "☐",
                "прогресс": 0,
                "категория": "🏠 Быт"  # ← категория по умолчанию
            })
            save_json(day_file, day_data)
            st.rerun()


def show_day_management(selected_day, day_data, day_file):
    """Управление днем - сохранение, копирование и т.д."""
    st.markdown("---")
    st.subheader("🛠️ Управление днем")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 Сохранить все изменения", use_container_width=True, type="primary"):
            save_json(day_file, day_data)
            st.success("✅ Все изменения сохранены!")

    with col2:
        if st.button("🔄 Обновить", use_container_width=True):
            st.rerun()

    with col3:
        # Создание нового дня на основе текущего
        if st.button("📅 Копировать день", use_container_width=True):
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_file = DIARY_DIR / f"{tomorrow}.json"

            # Копируем структуру, но сбрасываем прогресс
            copied_data = {
                "Утро": [{"задача": task["задача"], "время": task["время"], "статус": "☐", "прогресс": 0}
                         for task in day_data.get("Утро", [])],
                "День": [{"задача": task["задача"], "время": task["время"], "статус": "☐", "прогресс": 0}
                         for task in day_data.get("День", [])],
                "Вечер": [{"задача": task["задача"], "время": task["время"], "статус": "☐", "прогресс": 0}
                          for task in day_data.get("Вечер", [])],
                "Состояние": {},
                "Заметки": []
            }

            save_json(tomorrow_file, copied_data)
            st.success(f"📅 День на {tomorrow} создан как копия!")


def show_state_and_notes_editor(day_data, day_file, selected_day):
    """Редактор состояния и заметок"""
    with st.expander("💫 Настроить состояние и заметки", expanded=False):
        st.subheader("💫 Состояние")

        col1, col2 = st.columns(2)
        with col1:
            body = st.text_input("💪 Тело", value=day_data.get("Состояние", {}).get("💪 Тело", ""),
                                 placeholder="Состояние тела...")
            energy = st.text_input("🧘 Энергия", value=day_data.get("Состояние", {}).get("🧘 Энергия", ""),
                                   placeholder="Уровень энергии...")
            digestion = st.text_input("💨 Пищеварение", value=day_data.get("Состояние", {}).get("💨 Пищеварение", ""),
                                      placeholder="Пищеварение...")

        with col2:
            concentration = st.text_input("🧠 Концентрация",
                                          value=day_data.get("Состояние", {}).get("🧠 Концентрация", ""),
                                          placeholder="Уровень концентрации...")
            mood = st.text_input("🌿 Настроение", value=day_data.get("Состояние", {}).get("🌿 Настроение", ""),
                                 placeholder="Настроение...")
            weather_factor = st.text_input("🌦️ Фактор", value=day_data.get("Состояние", {}).get("🌦️ Фактор погоды", ""),
                                           placeholder="Внешние факторы...")

        st.subheader("📝 Заметки")
        notes_text = st.text_area("Заметки и инсайты дня (каждая с новой строки)",
                                  value="\n".join(day_data.get("Заметки", [])) if day_data.get("Заметки") else "",
                                  height=120,
                                  placeholder="Запишите ваши мысли, инсайты, наблюдения...")

        if st.button("💾 Сохранить состояние и заметки", use_container_width=True):
            # Сохраняем состояние
            day_data["Состояние"] = {
                "💪 Тело": body,
                "🧘 Энергия": energy,
                "💨 Пищеварение": digestion,
                "🧠 Концентрация": concentration,
                "🌿 Настроение": mood,
                "🌦️ Фактор погоды": weather_factor
            }

            # Сохраняем заметки
            if notes_text.strip():
                day_data["Заметки"] = [note.strip() for note in notes_text.split('\n') if note.strip()]
            else:
                day_data["Заметки"] = []

            save_json(day_file, day_data)
            st.success("✅ Состояние и заметки сохранены!")
            st.rerun()


def show_diary_tab():
    # Боковая панель - управление днями
    st.sidebar.header("📅 Управление днями")

    # Быстрый доступ к сегодня/завтра
    st.sidebar.subheader("⚡ Быстрый доступ")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        today_btn = st.button("📝 Сегодня", use_container_width=True)
    with col2:
        tomorrow_btn = st.button("🚀 Завтра", use_container_width=True)

    # Выбор дня для просмотра
    st.sidebar.subheader("🔍 Выбор дня")

    # Переключатель между календарем и списком
    view_mode = st.sidebar.radio("Режим просмотра:", ["📅 Календарь", "📋 Список дней"], horizontal=True)

    if view_mode == "📅 Календарь":
        selected_date = st.sidebar.date_input("Выберите день", value=date.today(), label_visibility="collapsed")
        selected_day = selected_date.strftime("%Y-%m-%d")
    else:
        # Старый вариант со списком
        all_days = sorted([f.stem for f in DIARY_DIR.glob("*.json")], reverse=True)
        if all_days:
            selected_day = st.sidebar.selectbox("Выберите день", all_days, key="day_selection",
                                                label_visibility="collapsed")
        else:
            selected_day = None

    # Обработка быстрых кнопок
    if today_btn:
        selected_day = date.today().strftime("%Y-%m-%d")
    if tomorrow_btn:
        selected_day = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        # Создаем день если его нет
        tomorrow_file = DIARY_DIR / f"{selected_day}.json"
        if not tomorrow_file.exists():
            empty_template = {"Утро": [], "День": [], "Вечер": [], "Состояние": {}, "Заметки": []}
            save_json(tomorrow_file, empty_template)

    # Создание нового дня
    st.sidebar.subheader("🆕 Создать новый день")

    daily_template_files = sorted(TEMPLATE_DIR.glob("*.json"))
    daily_template_names = [f.stem for f in daily_template_files]

    creation_type = st.sidebar.radio(
        "Тип дня:",
        ["📝 Пустой день", "🎯 Из шаблона"],
        key="day_creation_type"
    )

    new_day_name = st.sidebar.text_input("Название дня (YYYY-MM-DD)", placeholder="2025-10-15")

    if creation_type == "🎯 Из шаблона":
        selected_daily_template = st.sidebar.selectbox(
            "Шаблон дня",
            daily_template_names,
            key="daily_template"
        )

        if st.sidebar.button("📅 Создать из шаблона", use_container_width=True) and new_day_name:
            template_file = TEMPLATE_DIR / f"{selected_daily_template}.json"
            new_day_file = DIARY_DIR / f"{new_day_name}.json"
            copy_template(template_file, new_day_file)
            st.sidebar.success(f"День '{new_day_name}' создан из шаблона '{selected_daily_template}'!")
            selected_day = new_day_name
            st.rerun()

    else:  # Пустой день
        if st.sidebar.button("📄 Создать пустой день", use_container_width=True) and new_day_name:
            empty_template = {"Утро": [], "День": [], "Вечер": [], "Состояние": {}, "Заметки": []}
            new_day_file = DIARY_DIR / f"{new_day_name}.json"
            save_json(new_day_file, empty_template)
            st.sidebar.success(f"Пустой день '{new_day_name}' создан!")
            selected_day = new_day_name
            st.rerun()

    # Добавление новой задачи
    st.sidebar.subheader("➕ Быстрое добавление задачи")
    if selected_day:
        period_select = st.sidebar.selectbox("Период", ["Утро", "День", "Вечер"], key="new_task_period")
        task_name = st.sidebar.text_input("Название задачи", key="new_task_name", placeholder="Описание задачи...")
        task_time = st.sidebar.text_input("Время", key="new_task_time", placeholder="7:30-8:00")

        # БЛОК ВЫБОРА КАТЕГОРИИ - НОВОЕ
        if task_name:
            st.sidebar.subheader("🎯 Категория задачи")
            suggested_category = suggest_category(task_name)

            selected_category = st.sidebar.selectbox(
                "Категория",
                get_all_categories(),
                index=get_all_categories().index(
                    suggested_category) if suggested_category in get_all_categories() else 0,
                key="task_category_select",
                label_visibility="collapsed"
            )
            st.sidebar.caption(f"Автопредложение: {suggested_category}")

            if st.sidebar.button("Добавить задачу", use_container_width=True) and task_name and selected_day:
                day_file = DIARY_DIR / f"{selected_day}.json"
                day_data = load_day_data(selected_day)

                if period_select not in day_data:
                    day_data[period_select] = []

                day_data[period_select].append({
                    "задача": task_name,
                    "время": task_time,
                    "статус": "☐",
                    "прогресс": 0,
                    "категория": selected_category
                })
                save_json(day_file, day_data)
                st.sidebar.success("Задача добавлена!")
                st.rerun()

        # Основная область - работа с выбранным днем
        if selected_day:
            day_data = load_day_data(selected_day)
            day_file = DIARY_DIR / f"{selected_day}.json"

            st.header(f"📅 День: {selected_day}")

            show_tasks_compact("Утро", day_data["Утро"], selected_day, day_data, day_file)
            show_tasks_compact("День", day_data["День"], selected_day, day_data, day_file)
            show_tasks_compact("Вечер", day_data["Вечер"], selected_day, day_data, day_file)

            show_auto_analysis(day_data)

            if day_data.get("Состояние"):
                show_state_metrics(day_data["Состояние"])

            if day_data.get("Заметки"):
                show_notes(day_data["Заметки"])

            show_state_and_notes_editor(day_data, day_file, selected_day)

            show_day_management(selected_day, day_data, day_file)

        else:
            all_days = sorted([f.stem for f in DIARY_DIR.glob("*.json")], reverse=True)
            if not all_days:
                st.info("""
                ## 📅 Добро пожаловать в ежедневник!

                Здесь вы можете:
                - 📝 Создавать расписания на день
                - 🎯 Использовать шаблоны для разных типов дней
                - ✅ Отслеживать выполнение задач с прогресс-барами
                - ⏰ Планировать время по периодам дня
                - 📊 Видеть статистику по категориям задач
                - 💫 Отслеживать состояние и самочувствие
                - 📝 Записывать заметки и инсайты

                Чтобы начать, создайте ваш первый день в боковой панели!
                """)
            else:
                st.info("👈 Выберите день для просмотра в боковой панели")