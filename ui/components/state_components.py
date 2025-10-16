import streamlit as st
from typing import List, Dict
from models.state import StateCategory, DayState


class StateComponents:
    """Компоненты для работы с состоянием"""

    @staticmethod
    def render_state_editor(day_state: DayState, categories: List[StateCategory]) -> None:
        """Рендеринг редактора состояния"""

        if not categories:
            st.info("📊 Категории состояния не настроены")
            return

        # Сетка 2 колонки для лучшего расположения
        cols = st.columns(2)

        for i, category in enumerate(categories):
            with cols[i % 2]:  # Чередуем колонки
                StateComponents._render_single_state_field(day_state, category)

    @staticmethod
    def _render_single_state_field(day_state: DayState, category: StateCategory) -> None:
        """Рендеринг поля для одной категории состояния"""

        current_value = day_state.get_value(category.name) or ""

        # Заголовок с эмодзи
        st.markdown(f"**{category.emoji} {category.name}**")

        if category.type == "percent":
            # Проценты с ползунком
            default_value = int(current_value) if current_value and current_value.replace('%', '').isdigit() else 50
            value = st.slider(
                category.description,
                min_value=0,
                max_value=100,
                value=default_value,
                key=f"state_{category.name}"
            )
            display_value = f"{value}%"
            st.caption(f"🎯 {value}%")

        elif category.type == "scale_1_10":
            # Шкала 1-10
            default_value = int(current_value) if current_value and current_value.isdigit() and 1 <= int(
                current_value) <= 10 else 5
            value = st.select_slider(
                category.description,
                options=list(range(1, 11)),
                value=default_value,
                key=f"state_{category.name}"
            )
            # Визуальная шкала
            emoji_scale = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            display_value = f"{emoji_scale[value - 1]} {value}/10"
            st.caption(display_value)

        elif category.type == "text":
            # Текстовый ввод
            value = st.text_input(
                category.description,
                value=current_value,
                key=f"state_{category.name}",
                placeholder="Опишите состояние..."
            )
            display_value = value

        elif category.type == "yes_no":
            # Да/Нет
            options = ["✅ Да", "❌ Нет"]
            default_index = 0 if current_value == "✅ Да" else 1
            value = st.radio(
                category.description,
                options,
                index=default_index,
                key=f"state_{category.name}",
                horizontal=True
            )
            display_value = value

        # Сохраняем значение в состоянии
        if value != current_value:
            day_state.set_value(category.name, display_value, category.type)

    @staticmethod
    def render_state_summary(day_state: DayState, categories: List[StateCategory]) -> None:
        """Отображение сводки состояния"""
        if not day_state.values:
            st.info("📝 Состояние еще не оценено")
            return

        st.subheader("📊 Сводка состояния")

        summary_text = ""
        for category in categories:
            value = day_state.get_value(category.name)
            if value:
                summary_text += f"{category.emoji} **{category.name}:** {value}\n\n"

        if summary_text:
            st.markdown(summary_text)
        else:
            st.info("ℹ️ Заполните состояние выше")