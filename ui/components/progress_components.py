import streamlit as st
from typing import Dict, List


class ProgressComponents:
    """Компоненты для отображения прогресса"""

    @staticmethod
    def progress_bar(percent: int, width: int = 20) -> str:
        """Текстовый прогресс-бар"""
        filled = "█" * (percent * width // 100)
        empty = "░" * (width - len(filled))
        return f"{filled}{empty} {percent}%"

    @staticmethod
    def progress_bar_short(percent: int) -> str:
        """Короткий прогресс-бар"""
        filled = "█" * (percent // 20)
        empty = "░" * (5 - percent // 20)
        return f"{filled}{empty} {percent}%"

    @staticmethod
    def get_progress_emoji(progress: int) -> str:
        """Эмодзи для прогресса"""
        if progress == 100:
            return "🟩"
        elif progress >= 80:
            return "🟨"
        elif progress >= 50:
            return "🟧"
        else:
            return "🟥"

    @staticmethod
    def render_category_progress(category_progress: Dict[str, int]) -> None:
        """Отображение прогресса по категориям"""
        if not category_progress:
            st.info("🤔 Недостаточно данных для анализа категорий")
            return

        summary_md = "| Категория | Прогресс | Статус |\n|-----------|:---------:|:-------:|\n"

        for cat_name, avg in sorted(category_progress.items(), key=lambda x: x[1], reverse=True):
            if avg >= 90:
                status = "✅ Завершено"
            elif avg >= 70:
                status = "🟢 Хорошо"
            elif avg >= 50:
                status = "🟡 В процессе"
            else:
                status = "🔴 Начато"

            summary_md += f"| {cat_name} | {ProgressComponents.progress_bar(avg)} | {status} |\n"

        st.markdown(summary_md)
        st.caption("💡 На основе выбранных категорий задач")

    @staticmethod
    def render_section_progress(section_name: str, tasks: List, progress: int) -> None:
        """Отображение прогресса секции"""
        st.markdown(f"### {section_name}")
        st.markdown(f"`{ProgressComponents.progress_bar(progress)}` **{progress}%**")

        for task in tasks:
            task_name = task.get('название', '')
            task_progress = task.get('прогресс', 0)
            emoji = ProgressComponents.get_progress_emoji(task_progress)

            col1, col2 = st.columns([3, 2])
            with col1:
                st.write(f"{emoji} **{task_name}**")
            with col2:
                st.write(f"`{ProgressComponents.progress_bar_short(task_progress)}`")