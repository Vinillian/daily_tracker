import streamlit as st
from typing import List, Callable, Optional
from models.diary import Task
from core.constants import CATEGORIES, TASK_STATUSES


class TaskComponents:
    """Компоненты для работы с задачами"""

    @staticmethod
    def render_task_editor(
            task: Task,
            key_prefix: str,
            on_delete: Optional[Callable] = None,
            show_category: bool = True
    ) -> Task:
        """Рендеринг редактора одной задачи"""
        cols = st.columns([3, 2, 2, 2, 2, 1] if show_category else [3, 2, 2, 2, 1])

        col_index = 0

        with cols[col_index]:
            task.task = st.text_input(
                "Задача",
                value=task.task,
                key=f"{key_prefix}_task",
                label_visibility="collapsed",
                placeholder="Название задачи..."
            )
        col_index += 1

        with cols[col_index]:
            task.time = st.text_input(
                "Время",
                value=task.time,
                key=f"{key_prefix}_time",
                label_visibility="collapsed",
                placeholder="Время..."
            )
        col_index += 1

        if show_category:
            with cols[col_index]:
                current_category = task.category
                category_index = CATEGORIES.index(current_category) if current_category in CATEGORIES else 0
                task.category = st.selectbox(
                    "Категория",
                    CATEGORIES,
                    index=category_index,
                    key=f"{key_prefix}_category",
                    label_visibility="collapsed"
                )
            col_index += 1

        with cols[col_index]:
            status_index = TASK_STATUSES.index(task.status) if task.status in TASK_STATUSES else 0
            task.status = st.selectbox(
                "Статус",
                TASK_STATUSES,
                index=status_index,
                key=f"{key_prefix}_status",
                label_visibility="collapsed"
            )
        col_index += 1

        with cols[col_index]:
            task.progress = st.slider(
                "Прогресс",
                min_value=0,
                max_value=100,
                value=task.progress,
                key=f"{key_prefix}_progress",
                label_visibility="collapsed"
            )
        col_index += 1

        with cols[col_index]:
            if on_delete and st.button("❌", key=f"{key_prefix}_delete"):
                on_delete()

        return task
    @staticmethod
    def render_task_compact(task: Task) -> None:
        """Компактное отображение задачи (только чтение)"""
        progress_emoji = "🟢" if task.прогресс == 100 else "🟡" if task.прогресс >= 50 else "🔴"

        st.write(f"{progress_emoji} **{task.задача}**")
        st.caption(f"⏰ {task.время} | 🏷️ {task.категория} | 📊 {task.прогресс}% | {task.статус}")

    @staticmethod
    def render_new_task_form(period: str, on_add: Callable) -> None:
        """Форма добавления новой задачи"""
        with st.form(key=f"new_task_form_{period}", clear_on_submit=True):
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                task_name = st.text_input(
                    "Название задачи",
                    key=f"new_task_name_{period}",
                    placeholder="Описание задачи..."
                )

            with col2:
                task_time = st.text_input(
                    "Время",
                    key=f"new_task_time_{period}",
                    placeholder="09:00–10:00"
                )

            with col3:
                st.markdown("")  # Отступ для выравнивания
                if st.form_submit_button("➕ Добавить", use_container_width=True):
                    if task_name.strip():
                        new_task = Task(
                            задача=task_name.strip(),
                            время=task_time.strip() or "09:00–10:00",
                            статус="☐",
                            прогресс=0,
                            категория="🏠 Быт"
                        )
                        on_add(new_task)