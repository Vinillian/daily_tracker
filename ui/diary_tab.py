import streamlit as st
from datetime import date, timedelta
from typing import List, Optional
from core.constants import DAY_PERIODS, PERIOD_ICONS
from core.exceptions import DailyTrackerError
from services.diary_service import diary_service
from models.diary import Day, Task
from ui.components.task_components import TaskComponents
from ui.components.progress_components import ProgressComponents
from ui.components.time_components import TimeComponents
from core.constants import CATEGORIES, TASK_STATUSES
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
                    # Создаем день из шаблона и сразу сохраняем
                    day_data = diary_service.create_day(new_day_name, selected_template)
                    diary_service.save_day(new_day_name, day_data)
                    st.sidebar.success(f"День '{new_day_name}' создан из шаблона '{selected_template}'!")
                    st.rerun()
                except DailyTrackerError as e:
                    st.sidebar.error(f"Ошибка: {e}")

    def _render_quick_task_add(self, selected_day: str) -> None:
        """Быстрое добавление задачи с улучшенным выбором времени"""
        st.sidebar.subheader("➕ Быстрое добавление задачи")

        period_select = st.sidebar.selectbox(
            "Период",
            DAY_PERIODS,
            key="new_task_period_quick_add"  # ИЗМЕНИЛИ
        )
        task_name = st.sidebar.text_input(
            "Название задачи",
            key="new_task_name_quick_add",  # ИЗМЕНИЛИ
            placeholder="Описание задачи..."
        )

        # Используем улучшенный селектор времени с уникальным ключом
        task_time = TimeComponents.render_time_selector(key_suffix="quick_add_sidebar")  # ИЗМЕНИЛИ

        category_select = st.sidebar.selectbox(
            "Категория",
            CATEGORIES,
            key="new_task_category_quick_add"  # ИЗМЕНИЛИ
        )

        if st.sidebar.button("Добавить задачу", use_container_width=True,
                             key="add_task_quick_sidebar") and task_name and selected_day:
            try:
                day_data = diary_service.load_day(selected_day)
                new_task = Task(  # ⬅️ Автоматически получит ID
                    задача=task_name,
                    время=task_time or self._suggest_next_time([], period_select),
                    статус="☐",
                    прогресс=0,
                    категория=category_select
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
            # Проверяем существование дня перед загрузкой
            if not diary_service.day_exists(selected_day):
                st.warning(f"📅 День '{selected_day}' не найден")
                st.info("""
                **Чтобы создать этот день:**
                1. В боковой панели введите дату: `{selected_day}`
                2. Выберите тип дня (пустой или из шаблона)  
                3. Нажмите кнопку создания дня
                """.format(selected_day=selected_day))
                return

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
        """Рендеринг задач периода с использованием ID вместо индексов"""
        tasks = day_data.get_tasks_by_period(period)

        if tasks is None:
            tasks = []

        icon = PERIOD_ICONS.get(period, "📝")

        with st.expander(f"{icon} {period} ({len(tasks)} задач)", expanded=True):

            # Сортируем задачи для отображения
            sorted_tasks = self._sort_tasks_by_time(tasks)

            for display_index, task in enumerate(sorted_tasks):
                if task is None:
                    continue

                # ✅ СОЗДАЕМ CALLBACK'И С ФИКСИРОВАННЫМИ ID
                # Используем замыкание с параметром по умолчанию
                def create_delete_callback(task_id=task.id):
                    def delete_task():
                        # Удаляем задачу по ID
                        tasks[:] = [t for t in tasks if getattr(t, 'id', None) != task_id]
                        diary_service.save_day(selected_day, day_data)
                        st.rerun()

                    return delete_task

                def create_move_up_callback(task_id=task.id):
                    def move_up():
                        # Находим индекс задачи по ID
                        for i, t in enumerate(tasks):
                            if getattr(t, 'id', None) == task_id:
                                if i > 0:
                                    # Меняем местами с предыдущей задачей
                                    tasks[i], tasks[i - 1] = tasks[i - 1], tasks[i]
                                    diary_service.save_day(selected_day, day_data)
                                    st.rerun()
                                break

                    return move_up

                def create_move_down_callback(task_id=task.id):
                    def move_down():
                        # Находим индекс задачи по ID
                        for i, t in enumerate(tasks):
                            if getattr(t, 'id', None) == task_id:
                                if i < len(tasks) - 1:
                                    # Меняем местами со следующей задачей
                                    tasks[i], tasks[i + 1] = tasks[i + 1], tasks[i]
                                    diary_service.save_day(selected_day, day_data)
                                    st.rerun()
                                break

                    return move_down

                # ✅ ИСПОЛЬЗУЕМ ID В КЛЮЧАХ ДЛЯ УНИКАЛЬНОСТИ
                TaskComponents.render_task_editor(
                    task=task,
                    key_prefix=f"{selected_day}_{period}_{task.id}",  # ⬅️ Уникальный ключ с ID
                    on_delete=create_delete_callback(),
                    on_move_up=create_move_up_callback(),
                    on_move_down=create_move_down_callback(),
                    show_category=True,
                    show_move_buttons=True
                )

            # Кнопка добавления новой задачи (автоматически получит ID)
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"➕ Добавить задачу в {period}", key=f"add_{period}", use_container_width=True):
                    new_task = Task(
                        задача="Новая задача",
                        время=self._suggest_next_time(tasks, period),
                        статус="☐",
                        прогресс=0,
                        категория="🏠 Быт"
                    )
                    tasks.append(new_task)
                    diary_service.save_day(selected_day, day_data)
                    st.rerun()

            with col2:
                if st.button(f"🕐 Сортировать по времени", key=f"sort_{period}", use_container_width=True):
                    self._sort_tasks_in_period(tasks)
                    diary_service.save_day(selected_day, day_data)
                    st.rerun()

    def _render_day_analysis(self, day_data: Day) -> None:
        """Рендеринг анализа дня"""
        st.header("📊 Анализ дня по категориям")
        category_progress = day_data.calculate_category_progress()
        ProgressComponents.render_category_progress(category_progress)

    def _render_state_and_notes(self, day_data: Day, selected_day: str, day_file: str) -> None:
        """Рендеринг состояния и заметок"""

        with st.expander("💫 Состояние и заметки", expanded=False):

            # === БЛОК СОСТОЯНИЯ ===
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader("💫 Состояние")

            with col2:
                if st.button("⚙️ Управление категориями", use_container_width=True):
                    st.session_state['managing_categories'] = not st.session_state.get('managing_categories', False)

            # Проверяем что state существует
            if not hasattr(day_data, 'state'):
                from models.state import DayState
                day_data.state = DayState()

            # Загружаем категории состояния
            try:
                from services.state_service import state_service
                state_categories = state_service.load_categories()

                # Переключатель между управлением категориями и вводом состояния
                if st.session_state.get('managing_categories', False):
                    from ui.components.state_components import StateComponents
                    StateComponents.render_category_management()
                else:
                    # Сохраняем текущее состояние перед рендерингом
                    current_state_data = day_data.state.model_dump(by_alias=True) if hasattr(day_data.state,
                                                                                             'model_dump') else day_data.state.dict(
                        by_alias=True)

                    # Рендерим редактор состояния
                    from ui.components.state_components import StateComponents
                    StateComponents.render_state_editor(day_data.state, state_categories)

                    # Показываем сводку
                    StateComponents.render_state_summary(day_data.state, state_categories)

                    # Автосохранение при изменении состояния
                    new_state_data = day_data.state.model_dump(by_alias=True) if hasattr(day_data.state,
                                                                                         'model_dump') else day_data.state.dict(
                        by_alias=True)
                    if current_state_data != new_state_data:
                        try:
                            diary_service.save_day(selected_day, day_data)
                            st.success("✅ Состояние сохранено!")
                        except Exception as e:
                            st.error(f"Ошибка сохранения состояния: {e}")

            except Exception as e:
                st.error(f"Ошибка загрузки категорий состояния: {e}")
                st.info("⚠️ Используются категории по умолчанию")

                # Fallback - простые поля
                col1, col2 = st.columns(2)
                with col1:
                    energy = st.slider("💪 Энергия", 0, 100, 50)
                    focus = st.slider("🧠 Фокус", 0, 100, 50)
                with col2:
                    mood = st.slider("😌 Настроение", 0, 100, 50)
                    sleep = st.slider("🛌 Качество сна", 0, 100, 50)
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

    def _sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Сортировка задач по времени"""
        return sorted(tasks, key=lambda task: self._get_task_start_time(task))

    def _get_task_start_time(self, task: Task) -> str:
        """Получить время начала задачи для сортировки"""
        start_time, _ = TimeComponents.parse_time_range(task.time)
        return start_time or "23:59"  # Задачи без времени в конец

    def _sort_tasks_in_period(self, tasks: List[Task]) -> None:
        """Сортировка задач в периоде по времени"""
        tasks.sort(key=lambda task: self._get_task_start_time(task))

    def _suggest_next_time(self, tasks: List[Task], period: str) -> str:
        """Предложить следующее время для новой задачи"""
        if not tasks:
            # Первая задача в периоде
            if period == "Утро":
                return "07:00-08:00"
            elif period == "День":
                return "12:00-13:00"
            else:
                return "18:00-19:00"

        # Находим последнюю задачу по времени
        sorted_tasks = self._sort_tasks_by_time(tasks)
        last_task = sorted_tasks[-1]
        last_start, last_end = TimeComponents.parse_time_range(last_task.time)

        if last_end:
            # Предлагаем время после последней задачи
            try:
                # Простая логика - добавляем 1 час
                end_hour = int(last_end.split(':')[0])
                next_hour = (end_hour + 1) % 24
                return f"{last_end}-{next_hour:02d}:00"
            except:
                pass

        # Fallback
        return "09:00-10:00"


# Глобальный экземпляр
diary_tab = DiaryTab()