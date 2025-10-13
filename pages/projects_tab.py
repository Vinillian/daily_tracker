import streamlit as st
from pathlib import Path
from utils.file_utils import load_json, save_json, copy_template, ensure_dir
from utils.project_utils import get_project_tasks, get_project_sections

DATA_DIR = Path("data")
PROJECTS_DIR = DATA_DIR / "projects"
PROJECT_TEMPLATES_DIR = Path("templates/project_templates")

ensure_dir(PROJECTS_DIR)


def get_progress_emoji(progress):
    """Возвращает эмодзи в зависимости от прогресса"""
    if progress == 100:
        return "🟩"
    elif progress >= 80:
        return "🟨"
    elif progress >= 50:
        return "🟧"
    else:
        return "🟥"


def get_progress_bar(progress, width=20):
    """Создает текстовый прогресс-бар"""
    filled = int(progress * width / 100)
    empty = width - filled
    return "█" * filled + "░" * empty


def get_section_status_emojis(tasks):
    """Создает строку эмодзи для статуса секции"""
    emojis = []
    for task in tasks:
        progress = task.get('прогресс', 0)
        emojis.append(get_progress_emoji(progress))

    # Дополняем до 5 эмодзи для единообразия
    while len(emojis) < 5:
        emojis.append("⬜")

    return " ".join(emojis[:5])


def calculate_section_progress(tasks):
    """Вычисляет средний прогресс по секции"""
    if not tasks:
        return 0
    total = sum(task.get('прогресс', 0) for task in tasks)
    return total // len(tasks)


def show_project_dashboard(project_data, project_name):
    """Отображает дэшборд проекта"""

    # Заголовок
    metadata = project_data.get('metadata', {})
    st.header(f"🚀 {metadata.get('название', project_name)} — {metadata.get('версия', 'v1.0.0')}")
    st.caption(metadata.get('описание', 'Обзор статуса проекта'))

    # Основные секции
    sections = get_project_sections(project_data)

    for section_name, tasks in sections.items():
        section_progress = calculate_section_progress(tasks)
        status_emojis = get_section_status_emojis(tasks)

        st.markdown(f"### {section_name}")

        # Прогресс-бар секции
        progress_bar = get_progress_bar(section_progress)
        st.markdown(f"`{progress_bar}` **{section_progress}%**")

        # Задачи секции
        for task in tasks:
            task_name = task.get('название', '')
            task_progress = task.get('прогресс', 0)
            emoji = get_progress_emoji(task_progress)

            # Создаем строку точек для выравнивания
            dots = "." * (40 - len(task_name))

            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{emoji} **{task_name}** {dots}")
            with col2:
                st.write(f"**{task_progress}%**")

        st.markdown("---")

    # Общая статистика
    overall = project_data.get('overall', {})
    if overall:
        st.markdown("### 🏁 OVERALL PROJECT STATUS")

        # Глобальный прогресс
        global_progress = overall.get('GLOBAL_PROGRESS', 0)
        st.markdown(f"**📈 GLOBAL PROGRESS:**    `{get_progress_bar(global_progress)}` {global_progress}%")

        # Стабильность
        stability = overall.get('STABILITY_INDEX', 0)
        st.markdown(f"**🧠 STABILITY INDEX:**    `{get_progress_bar(stability)}` {stability}%")

        # Производительность
        performance = overall.get('PERFORMANCE_BOOST', 0)
        st.markdown(f"**⚙️ PERFORMANCE BOOST:**  {'🟩' * 5} +{performance}%")

        # Мобильная готовность
        mobile_ready = overall.get('MOBILE_READY', False)
        mobile_status = "✅ YES" if mobile_ready else "❌ NO"
        st.markdown(f"**📱 MOBILE READY:**       {mobile_status}")

        # Веб-режим
        web_mode = overall.get('WEB_MODE', '')
        st.markdown(f"**🌐 WEB MODE:**           {web_mode}")


def show_projects_tab():
    # Получаем списки проектов и шаблонов
    all_projects = sorted([f.stem for f in PROJECTS_DIR.glob("*.json")], reverse=True)
    project_template_files = sorted(PROJECT_TEMPLATES_DIR.glob("*.json"))
    project_template_names = [f.stem for f in project_template_files]

    # Боковая панель для управления проектами
    st.sidebar.header("📁 Управление проектами")

    # Создание нового проекта
    st.sidebar.subheader("Создать новый проект")

    # Выбор типа создания
    creation_type = st.sidebar.radio(
        "Тип проекта:",
        ["📝 Пустой проект", "🎯 Из шаблона"],
        key="project_creation_type"
    )

    new_project_name = st.sidebar.text_input("Название нового проекта")

    if creation_type == "🎯 Из шаблона":
        selected_template = st.sidebar.selectbox(
            "Выберите шаблон",
            project_template_names,
            key="template_selection"
        )

        if st.sidebar.button("🚀 Создать из шаблона", use_container_width=True):
            if new_project_name and selected_template:
                template_file = PROJECT_TEMPLATES_DIR / f"{selected_template}.json"
                new_project_file = PROJECTS_DIR / f"{new_project_name}.json"
                copy_template(template_file, new_project_file)
                st.sidebar.success(f"Проект '{new_project_name}' создан из шаблона '{selected_template}'!")
                st.rerun()
            else:
                st.sidebar.error("Введите название проекта и выберите шаблон")

    else:  # Пустой проект
        if st.sidebar.button("📄 Создать пустой проект", use_container_width=True):
            if new_project_name:
                empty_project = {
                    "metadata": {
                        "название": new_project_name,
                        "версия": "v1.0.0",
                        "дата": "{{дата}}",
                        "описание": "Новый проект"
                    },
                    "sections": [
                        {
                            "название": "📋 Планирование",
                            "задачи": [
                                {"название": "Определение требований", "прогресс": 0},
                                {"название": "Проектирование архитектуры", "прогресс": 0}
                            ]
                        }
                    ]
                }
                new_project_file = PROJECTS_DIR / f"{new_project_name}.json"
                save_json(new_project_file, empty_project)
                st.sidebar.success(f"Пустой проект '{new_project_name}' создан!")
                st.rerun()
            else:
                st.sidebar.error("Введите название проекта")

    # Выбор проекта для просмотра
    st.sidebar.subheader("📊 Просмотр проектов")

    if not all_projects:
        st.sidebar.info("📝 Проектов пока нет. Создайте первый проект!")
        selected_project = None
    else:
        selected_project = st.sidebar.selectbox(
            "Выберите проект",
            all_projects,
            key="project_selection"
        )

    # Основная область - отображение проектов
    if selected_project:
        project_file = PROJECTS_DIR / f"{selected_project}.json"
        project_data = load_json(project_file)

        # Переключатель между дэшбордом и редактированием
        view_mode = st.radio(
            "Режим просмотра:",
            ["📊 Дэшборд", "✏️ Редактирование"],
            horizontal=True,
            key=f"view_mode_{selected_project}"
        )

        if view_mode == "📊 Дэшборд":
            show_project_dashboard(project_data, selected_project)
        else:
            # Режим редактирования
            st.subheader(f"✏️ Редактирование: {selected_project}")

            # Отображение метаданных
            metadata = project_data.get('metadata', {})
            st.markdown("### 📋 Метаданные проекта")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text_input("Название", value=metadata.get('название', ''), key="meta_name")
            with col2:
                st.text_input("Версия", value=metadata.get('версия', 'v1.0.0'), key="meta_version")
            with col3:
                st.text_input("Описание", value=metadata.get('описание', ''), key="meta_description")

            # Отображение секций и задач
            sections = get_project_sections(project_data)

            for section_name, tasks in sections.items():
                st.markdown(f"### 📁 {section_name}")

                for i, task in enumerate(tasks):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text_input(
                            "Название задачи",
                            value=task['название'],
                            key=f"task_{section_name}_{i}_name"
                        )
                    with col2:
                        new_progress = st.number_input(
                            "Прогресс %",
                            min_value=0,
                            max_value=100,
                            value=task.get('прогресс', 0),
                            key=f"task_{section_name}_{i}_progress"
                        )

                    # Обновляем прогресс в данных
                    task['прогресс'] = new_progress

            # Кнопка сохранения
            if st.button("💾 Сохранить изменения", use_container_width=True):
                save_json(project_file, project_data)
                st.success("✅ Изменения сохранены!")

    else:
        # Экран при отсутствии проектов
        if not all_projects:
            st.info("""
            ## 🚀 Добро пожаловать в менеджер проектов!

            Здесь вы можете:
            - 📊 **Отслеживать прогресс** ваших проектов
            - 🎯 **Создавать проекты** из шаблонов или с нуля
            - 📈 **Визуализировать** статус выполнения задач

            **Чтобы начать, создайте ваш первый проект в боковой панели!**
            """)
        else:
            st.info("👈 Выберите проект для просмотра в боковой панели")