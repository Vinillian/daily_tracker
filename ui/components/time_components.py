import streamlit as st
from typing import List, Tuple, Optional
from core.constants import TIME_SLOTS, POPULAR_TIME_RANGES


class TimeComponents:
    """Компоненты для работы со временем"""

    @staticmethod
    def render_time_selector(current_time: str = "", key_suffix: str = "") -> str:
        """Компонент выбора временного интервала с уникальным ключом"""

        # Создаем уникальный ключ
        base_key = f"time_selector_{key_suffix}" if key_suffix else "time_selector_default"

        # Используем session_state для хранения выбранного времени
        if f"{base_key}_value" not in st.session_state:
            st.session_state[f"{base_key}_value"] = current_time

        col1, col2 = st.columns([2, 1])
        result_time = current_time

        with col1:
            # Основной выбор из популярных диапазонов
            time_options = ["Выберите время..."] + POPULAR_TIME_RANGES + ["Другой интервал..."]

            # Находим индекс текущего времени
            current_index = 0
            if current_time:
                for i, option in enumerate(time_options):
                    if option == current_time:
                        current_index = i
                        break

            selected_option = st.selectbox(
                "Временной интервал",
                options=time_options,
                index=current_index,
                key=f"{base_key}_main"
            )

            if selected_option == "Другой интервал...":
                # Кастомный ввод времени
                custom_time = st.text_input(
                    "Введите время вручную (например: 09:00-10:30)",
                    value=current_time if current_time and current_time not in POPULAR_TIME_RANGES else "",
                    placeholder="09:00-10:30",
                    key=f"{base_key}_custom"
                )
                if custom_time:
                    result_time = custom_time
            elif selected_option != "Выберите время...":
                result_time = selected_option

        with col2:
            # Быстрые кнопки для часто используемых времен
            st.markdown("**Быстро:**")
            quick_col1, quick_col2 = st.columns(2)

            with quick_col1:
                if st.button("🕘 1ч", use_container_width=True, key=f"{base_key}_1h"):
                    result_time = "09:00-10:00"
                if st.button("🕛 30м", use_container_width=True, key=f"{base_key}_30m"):
                    result_time = "09:00-09:30"

            with quick_col2:
                if st.button("🕑 2ч", use_container_width=True, key=f"{base_key}_2h"):
                    result_time = "14:00-16:00"
                if st.button("🕔 15м", use_container_width=True, key=f"{base_key}_15m"):
                    result_time = "17:00-17:15"

        # Обновляем session_state
        if result_time != current_time:
            st.session_state[f"{base_key}_value"] = result_time

        return result_time

    @staticmethod
    def _find_time_option_index(time_str: str, options: List[str]) -> int:
        """Найти индекс временного интервала в списке опций"""
        if not time_str:
            return 0

        for i, option in enumerate(options):
            if option == time_str:
                return i

        # Если время не найдено в популярных, выбираем "Другой интервал..."
        return len(options) - 2 if len(options) > 2 else 0

    @staticmethod
    def parse_time_range(time_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Парсинг временного диапазона в start_time и end_time"""
        if not time_str:
            return None, None

        # Поддерживаем разные разделители
        separators = ['–', '-', '—', ' to ', ' до ']
        for sep in separators:
            if sep in time_str:
                parts = time_str.split(sep)
                if len(parts) == 2:
                    start = parts[0].strip()
                    end = parts[1].strip()
                    # Нормализуем формат времени
                    start = TimeComponents._normalize_time(start)
                    end = TimeComponents._normalize_time(end)
                    return start, end

        return None, None

    @staticmethod
    def _normalize_time(time_str: str) -> str:
        """Нормализация формата времени"""
        if not time_str:
            return ""

        # Убираем лишние пробелы
        time_str = time_str.strip()

        # Добавляем ведущий ноль если нужно
        if len(time_str) == 4 and time_str[1] == ':':
            time_str = '0' + time_str

        return time_str

    @staticmethod
    def compare_times(time1: str, time2: str) -> int:
        """Сравнение двух временных интервалов для сортировки"""
        start1, _ = TimeComponents.parse_time_range(time1)
        start2, _ = TimeComponents.parse_time_range(time2)

        if not start1 and not start2:
            return 0
        elif not start1:
            return 1
        elif not start2:
            return -1

        # Сравниваем по начальному времени
        return (start1 > start2) - (start1 < start2)