import streamlit as st
from typing import List, Optional
from core.exceptions import DailyTrackerError
from services.project_service import project_service
from models.projects import Project, ProjectTask, ProjectSection
from ui.components.progress_components import ProgressComponents


class ProjectsTab:
    """Вкладка проектов"""

    def __init__(self):
        self.template_files = project_service.template_dir.glob("*.json")
        self.template_names = sorted([f.stem for f in self.template_files])

    def render_sidebar(self) -> Optional[str]:
        """Рендеринг боковой панели"""
        st.sidebar.header("📁 Управление проектами")

        # Создание проекта
        st.sidebar.subheader("Создать новый проект")

        creation_type = st.sidebar.radio(
            "Тип проекта:",
            ["📝 Пустой проект", "🎯 Из шаблона"],
            key="project_creation_type"
        )

        new_project_name = st.sidebar.text_input("Название нового проекта")

        if creation_type == "🎯 Из шаблона":
            selected_template = st.sidebar.selectbox(
                "Выберите шаблон",
                self.template_names,
                key="template_selection"
            )

            if st.sidebar.button("🚀 Создать из шаблона", use_container_width=True):
                if new_project_name and selected_template:
                    try:
                        project_service.create_project(new_project_name, selected_template)
                        project_service.save_project(new_project_name, project_service.load_project(new_project_name))
                        st.sidebar.success(f"Проект '{new_project_name}' создан из шаблона!")
                        st.rerun()
                    except DailyTrackerError as e:
                        st.sidebar.error(f"Ошибка: {e}")
                else:
                    st.sidebar.error("Введите название проекта и выберите шаблон")
        else:
            if st.sidebar.button("📄 Создать пустой проект", use_container_width=True):
                if new_project_name:
                    try:
                        project_service.create_project(new_project_name)
                        project_service.save_project(new_project_name, project_service.load_project(new_project_name))
                        st.sidebar.success(f"Пустой проект '{new_project_name}' создан!")
                        st.rerun()
                    except DailyTrackerError as e:
                        st.sidebar.error(f"Ошибка: {e}")
                else:
                    st.sidebar.error("Введите название проекта")

        # Выбор проекта
        st.sidebar.subheader("📊 Просмотр проектов")
        all_projects = project_service.list_projects()

        if not all_projects:
            st.sidebar.info("📝 Проектов пока нет. Создайте первый проект!")
            return None

        selected_project = st.sidebar.selectbox(
            "Выберите проект",
            all_projects,
            key="project_selection"
        )

        return selected_project

    def render_project_content(self, project_name: str) -> None:
        """Рендеринг содержимого проекта"""
        try:
            project_data = project_service.load_project(project_name)

            # Переключатель режимов
            view_mode = st.radio(
                "Режим просмотра:",
                ["📊 Дэшборд", "✏️ Редактирование"],
                horizontal=True,
                key=f"view_mode_{project_name}"
            )

            if view_mode == "📊 Дэшборд":
                self._render_project_dashboard(project_data, project_name)
            else:
                self._render_project_editor(project_data, project_name)

        except DailyTrackerError as e:
            st.error(f"Ошибка загрузки проекта: {e}")

    def _render_project_dashboard(self, project_data: Project, project_name: str) -> None:
        """Рендеринг дэшборда проекта"""
        metadata = project_data.metadata
        st.header(f"🚀 {metadata.название} — {metadata.версия}")
        st.caption(metadata.описание)

        # Секции проекта
        for section in project_data.sections:
            section_progress = section.calculate_section_progress()
            ProgressComponents.render_section_progress(
                section.название,
                [task.dict() for task in section.задачи],
                section_progress
            )

        # Общая статистика
        self._render_overall_stats(project_data.overall)

    def _render_overall_stats(self, overall) -> None:
        """Рендеринг общей статистики"""
        st.markdown("### 🏁 OVERALL PROJECT STATUS")

        st.markdown(
            f"**📈 GLOBAL PROGRESS:**    `{ProgressComponents.progress_bar(overall.глобальный_прогресс)}` {overall.глобальный_прогресс}%")
        st.markdown(
            f"**🧠 STABILITY INDEX:**    `{ProgressComponents.progress_bar(overall.индекс_стабильности)}` {overall.индекс_стабильности}%")
        st.markdown(f"**⚙️ PERFORMANCE BOOST:**  {'🟩' * 5} +{overall.прирост_производительности}%")

        mobile_status = "✅ YES" if overall.мобильная_готовность else "❌ NO"
        st.markdown(f"**📱 MOBILE READY:**       {mobile_status}")
        st.markdown(f"**🌐 WEB MODE:**           {overall.веб_режим}")

    def _render_project_editor(self, project_data: Project, project_name: str) -> None:
        """Рендеринг редактора проекта"""
        st.subheader(f"✏️ Редактирование: {project_name}")

        # Метаданные
        st.markdown("### 📋 Метаданные проекта")
        col1, col2, col3 = st.columns(3)

        with col1:
            new_name = st.text_input("Название", value=project_data.metadata.название, key="meta_name")
        with col2:
            new_version = st.text_input("Версия", value=project_data.metadata.версия, key="meta_version")
        with col3:
            new_description = st.text_input("Описание", value=project_data.metadata.описание, key="meta_description")

        project_data.metadata.название = new_name
        project_data.metadata.версия = new_version
        project_data.metadata.описание = new_description

        # Секции и задачи
        st.markdown("### 🎯 Задачи проекта")

        for section_idx, section in enumerate(project_data.sections):
            section_progress = section.calculate_section_progress()

            st.markdown(f"#### 📁 {section.название}")
            st.markdown(
                f"**Общий прогресс секции:** `{ProgressComponents.progress_bar(section_progress)}` **{section_progress}%**")

            # Задачи секции
            for task_idx, task in enumerate(section.задачи):
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    new_task_name = st.text_input(
                        "Название задачи",
                        value=task.название,
                        key=f"task_{section_idx}_{task_idx}_name"
                    )
                    task.название = new_task_name

                with col2:
                    new_progress = st.slider(
                        "Прогресс",
                        min_value=0,
                        max_value=100,
                        value=task.прогресс,
                        key=f"task_{section_idx}_{task_idx}_progress"
                    )
                    task.прогресс = new_progress

                with col3:
                    st.markdown("")
                    st.markdown("")
                    if st.button("❌", key=f"delete_{section_idx}_{task_idx}"):
                        section.задачи.pop(task_idx)
                        project_service.save_project(project_name, project_data)
                        st.rerun()

            # Добавление новой задачи
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_task_name = st.text_input("Новая задача", key=f"new_task_{section_idx}_name")
            with col2:
                new_task_progress = st.number_input(
                    "Прогресс %",
                    min_value=0,
                    max_value=100,
                    value=0,
                    key=f"new_task_{section_idx}_progress"
                )
            with col3:
                st.markdown("")
                st.markdown("")
                if st.button("➕", key=f"add_{section_idx}") and new_task_name:
                    section.задачи.append(ProjectTask(
                        название=new_task_name,
                        прогресс=new_task_progress
                    ))
                    project_service.save_project(project_name, project_data)
                    st.rerun()

            st.markdown("---")

        # Общая статистика
        st.markdown("### 📊 Общая статистика")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            global_progress = st.slider(
                "Глобальный прогресс", 0, 100,
                project_data.overall.глобальный_прогресс, key="global_progress"
            )
        with col2:
            stability = st.slider(
                "Индекс стабильности", 0, 100,
                project_data.overall.индекс_стабильности, key="stability"
            )
        with col3:
            performance = st.number_input(
                "Прирост производительности %",
                value=project_data.overall.прирост_производительности, key="performance"
            )
        with col4:
            mobile_ready = st.checkbox(
                "Мобильная готовность",
                value=project_data.overall.мобильная_готовность, key="mobile_ready"
            )
        with col5:
            web_mode = st.selectbox(
                "Веб-режим",
                ["✅ Stable", "⚠️ IndexedDB unstable", "❌ Not supported"],
                index=["✅ Stable", "⚠️ IndexedDB unstable", "❌ Not supported"].index(
                    project_data.overall.веб_режим
                ) if project_data.overall.веб_режим in ["✅ Stable", "⚠️ IndexedDB unstable", "❌ Not supported"] else 1,
                key="web_mode"
            )

        project_data.overall.глобальный_прогресс = global_progress
        project_data.overall.индекс_стабильности = stability
        project_data.overall.прирост_производительности = performance
        project_data.overall.мобильная_готовность = mobile_ready
        project_data.overall.веб_режим = web_mode

        # Кнопка сохранения
        if st.button("💾 Сохранить все изменения", use_container_width=True):
            try:
                project_service.save_project(project_name, project_data)
                st.success("✅ Все изменения сохранены!")
            except DailyTrackerError as e:
                st.error(f"Ошибка сохранения: {e}")

    def render_empty_state(self) -> None:
        """Рендеринг пустого состояния"""
        st.info("""
        ## 🚀 Добро пожаловать в менеджер проектов!

        Здесь вы можете:
        - 📊 **Отслеживать прогресс** ваших проектов с графическими индикаторами
        - 🎯 **Создавать проекты** из шаблонов или с нуля
        - 📈 **Визуализировать** статус выполнения задач
        - ✏️ **Редактировать** задачи с ползунками прогресса
        - ❌ **Удалять** ненужные задачи

        **Чтобы начать, создайте ваш первый проект в боковой панели!**
        """)

    def show_projects_tab(self) -> None:
        """Основной метод отображения вкладки"""
        try:
            selected_project = self.render_sidebar()

            if selected_project:
                self.render_project_content(selected_project)
            else:
                if not project_service.list_projects():
                    self.render_empty_state()
                else:
                    st.info("👈 Выберите проект для просмотра в боковой панели")

        except Exception as e:
            st.error(f"Неожиданная ошибка: {e}")


# Глобальный экземпляр
projects_tab = ProjectsTab()