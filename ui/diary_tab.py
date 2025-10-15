import streamlit as st
from datetime import date, timedelta
from typing import List, Optional
from core.constants import DAY_PERIODS, PERIOD_ICONS
from core.exceptions import DailyTrackerError
from services.diary_service import diary_service
from models.diary import Day, Task
from ui.components.task_components import TaskComponents
from ui.components.progress_components import ProgressComponents


class DiaryTab:
    """Вкладка ежедневника"""

    def __init__(self):
        self.template_files = diary_service.template_dir.glob("*.json")
        self.template_names = sorted([f.stem for f in self.template_files])

    def render_sidebar(self) -> str:
        """Рендеринг боковой панели"""
        st.sidebar.header("📅 Управление днями")

        # Быстрый доступ
        st.sidebar.subheader("⚡ Быстрый доступ")
        col1, col2 = st.sidebar.columns(2)

        selected_day = None

        with col1:
            if st.button("📝 Сегодня", use_container_width=True):
                selected_day = date.today().strftime("%Y-%m-%d")

        with col2:
            if st.button("🚀 Завтра", use_container_width=True):
                selected_day = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Выбор дня
        st.sidebar.subheader("🔍 Выбор дня")
        view_mode = st.sidebar.radio(
            "Режим просмотра:",
            ["📅 Календарь", "📋 Список дней"],
            horizontal=True
        )

        if view_mode == "📅 Календарь":
            selected_date = st.sidebar.date_input(
                "Выберите день",
                value=date.today(),
                label_visibility="collapsed"
            )
            selected_day = selected_date.strftime("%Y-%m-%d")
        else:
            all_days = diary_service.list_days()
            if all_days:
                selected_day = st.sidebar.selectbox(
                    "Выберите день",
                    all_days,
                    label_visibility="collapsed"
                )

        # Создание нового дня
        self._render_day_creation()

        # Быстрое добавление задачи
        if selected_day:
            self._render_quick_task_add(selected_day)

        return selected_day

    def _render_day_creation(self) -> None:
        """Рендеринг создания нового дня"""
        st.sidebar.subheader("🆕 Создать новый день")

        creation_type = st.sidebar.radio(
            "Тип дня:",
            ["📝 Пустой день", "🎯 Из шаблона"],
            key="day_creation_type"
        )

        new_day_name = st.sidebar.text_input(
            "Название дня (YYYY-MM-DD)",
            placeholder="2025-10-15"
        )

        if creation_type == "🎯 Из шаблона":
            selected_template = st.sidebar.selectbox(
                "Шаблон дня",
                self.template_names,
                key="daily_template"
            )

            if st.sidebar.button("📅 Создать из шаблона", use_container_width=True) and new_day_name:
                try:
                    diary_service.create_day(new_day_name, selected_template)
                    st.sidebar.success(f"День '{new_day_name}' создан из шаблона!")
                    st.rerun()
                except DailyTrackerError as e:
                    st.sidebar.error(f"Ошибка: {e}")
        else:
            if st.sidebar.button("📄 Создать пустой день", use_container_width=True) and new_day_name:
                try:
                    diary_service.create_day(new_day_name)
                    diary_service.save_day(new_day_name, Day())
                    st.sidebar.success(f"Пустой день '{new_day_name}' создан!")
                    st.rerun()
                except DailyTrackerError as e:
                    st.sidebar.error(f"Ошибка: {e}")

    def _render_quick_task_add(self, selected_day: str) -> None:
        """Быстрое добавление задачи"""
        st.sidebar.subheader("➕ Быстрое добавление задачи")

        period_select = st.sidebar.selectbox(
            "Период",
            DAY_PERIODS,
            key="new_task_period"
        )
        task_name = st.sidebar.text_input(
            "Название задачи",
            key="new_task_name",
            placeholder="Описание задачи..."
        )
        task_time = st.sidebar.text_input(
            "Время",
            key="new_task_time",
            placeholder="09:00–10:00"
        )

        if st.sidebar.button("Добавить задачу", use_container_width=True) and task_name and selected_day:
            try:
                day_data = diary_service.load_day(selected_day)
                new_task = Task(
                    задача=task_name,
                    время=task_time or "09:00–10:00",
                    статус="☐",
                    прогресс=0,
                    категория="🏠 Быт"
                )
                day_data.add_task(period_select, new_task)
                diary_service.save_day(selected_day, day_data)
                st.sidebar.success("Задача добавлена!")
                st.rerun()
            except DailyTrackerError as e:
                st.sidebar.error(f"Ошибка: {e}")

    def render_day_content(self, selected_day: str) -> None:
        """Рендеринг содержимого дня"""
        try:
            day_data = diary_service.load_day(selected_day)
            day_file = diary_service.data_dir / f"{selected_day}.json"

            st.header(f"📅 День: {selected_day}")

            # Периоды дня
            for period in DAY_PERIODS:
                self._render_period_tasks(period, day_data, selected_day, day_file)

            # Анализ
            self._render_day_analysis(day_data)

            # Состояние и заметки
            self._render_state_and_notes(day_data, selected_day, day_file)

            # Управление днем
            self._render_day_management(selected_day, day_data, day_file)

        except DailyTrackerError as e:
            st.error(f"Ошибка загрузки дня: {e}")

    def _render_period_tasks(self, period: str, day_data: Day, selected_day: str, day_file: str) -> None:
        """Рендеринг задач периода"""
        tasks = day_data.get_tasks_by_period(period)
        icon = PERIOD_ICONS.get(period, "📝")

        with st.expander(f"{icon} {period} ({len(tasks)} задач)", expanded=True):
            for i, task in enumerate(tasks):
                def create_delete_callback(idx, period_tasks):
                    def delete_task():
                        period_tasks.pop(idx)
                        diary_service.save_day(selected_day, day_data)
                        st.rerun()

                    return delete_task

                TaskComponents.render_task_editor(
                    task=task,
                    key_prefix=f"{selected_day}_{period}_{i}",
                    on_delete=create_delete_callback(i, tasks),
                    show_category=True
                )

            # Кнопка добавления новой задачи
            if st.button(f"➕ Добавить в {period}", key=f"add_{period}", use_container_width=True):
                tasks.append(Task(
                    задача="Новая задача",
                    время="09:00–10:00",
                    статус="☐",
                    прогресс=0,
                    категория="🏠 Быт"
                ))
                diary_service.save_day(selected_day, day_data)
                st.rerun()

    def _render_day_analysis(self, day_data: Day) -> None:
        """Рендеринг анализа дня"""
        st.header("📊 Анализ дня по категориям")
        category_progress = day_data.calculate_category_progress()
        ProgressComponents.render_category_progress(category_progress)

    def _render_state_and_notes(self, day_data: Day, selected_day: str, day_file: str) -> None:
        """Рендеринг состояния и заметок"""
        with st.expander("💫 Настроить состояние и заметки", expanded=False):
            st.subheader("💫 Состояние")

            col1, col2 = st.columns(2)
            with col1:
                body = st.text_input(
                    "💪 Тело",
                    value=day_data.состояние.тело,
                    placeholder="Состояние тела..."
                )
                energy = st.text_input(
                    "🧘 Энергия",
                    value=day_data.состояние.энергия,
                    placeholder="Уровень энергии..."
                )
                digestion = st.text_input(
                    "💨 Пищеварение",
                    value=day_data.состояние.пищеварение,
                    placeholder="Пищеварение..."
                )

            with col2:
                concentration = st.text_input(
                    "🧠 Концентрация",
                    value=day_data.состояние.концентрация,
                    placeholder="Уровень концентрации..."
                )
                mood = st.text_input(
                    "🌿 Настроение",
                    value=day_data.состояние.настроение,
                    placeholder="Настроение..."
                )
                weather_factor = st.text_input(
                    "🌦️ Фактор",
                    value=day_data.состояние.фактор_погоды,
                    placeholder="Внешние факторы..."
                )

            st.subheader("📝 Заметки")
            notes_text = st.text_area(
                "Заметки и инсайты дня (каждая с новой строки)",
                value="\n".join(day_data.заметки) if day_data.заметки else "",
                height=120,
                placeholder="Запишите ваши мысли, инсайты, наблюдения..."
            )

            if st.button("💾 Сохранить состояние и заметки", use_container_width=True):
                try:
                    # Обновляем состояние
                    day_data.состояние.тело = body
                    day_data.состояние.энергия = energy
                    day_data.состояние.пищеварение = digestion
                    day_data.состояние.концентрация = concentration
                    day_data.состояние.настроение = mood
                    day_data.состояние.фактор_погоды = weather_factor

                    # Обновляем заметки
                    if notes_text.strip():
                        day_data.заметки = [note.strip() for note in notes_text.split('\n') if note.strip()]
                    else:
                        day_data.заметки = []

                    diary_service.save_day(selected_day, day_data)
                    st.success("✅ Состояние и заметки сохранены!")
                    st.rerun()
                except DailyTrackerError as e:
                    st.error(f"Ошибка сохранения: {e}")

    def _render_day_management(self, selected_day: str, day_data: Day, day_file: str) -> None:
        """Рендеринг управления днем"""
        st.markdown("---")
        st.subheader("🛠️ Управление днем")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("💾 Сохранить все изменения", use_container_width=True, type="primary"):
                try:
                    diary_service.save_day(selected_day, day_data)
                    st.success("✅ Все изменения сохранены!")
                except DailyTrackerError as e:
                    st.error(f"Ошибка сохранения: {e}")

        with col2:
            if st.button("🔄 Обновить", use_container_width=True):
                st.rerun()

        with col3:
            if st.button("📅 Копировать день", use_container_width=True):
                try:
                    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
                    diary_service.copy_day(selected_day, tomorrow)
                    st.success(f"📅 День на {tomorrow} создан как копия!")
                except DailyTrackerError as e:
                    st.error(f"Ошибка копирования: {e}")

    def render_empty_state(self) -> None:
        """Рендеринг пустого состояния"""
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

    def show_diary_tab(self) -> None:
        """Основной метод отображения вкладки"""
        try:
            selected_day = self.render_sidebar()

            if selected_day:
                self.render_day_content(selected_day)
            else:
                if not diary_service.list_days():
                    self.render_empty_state()
                else:
                    st.info("👈 Выберите день для просмотра в боковой панели")

        except Exception as e:
            st.error(f"Неожиданная ошибка: {e}")


# Глобальный экземпляр
diary_tab = DiaryTab()