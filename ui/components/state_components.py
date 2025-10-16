import streamlit as st
from typing import List
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
            # Проценты с ползунком - исправляем парсинг
            try:
                # Пытаемся извлечь число из строки "75%"
                if current_value and '%' in current_value:
                    clean_value = current_value.replace('%', '').strip()
                    default_value = int(clean_value) if clean_value.isdigit() else 50
                elif current_value and current_value.isdigit():
                    default_value = int(current_value)
                else:
                    default_value = 50
            except (ValueError, AttributeError):
                default_value = 50

            value = st.slider(
                f"Уровень {category.name.lower()}",
                min_value=0,
                max_value=100,
                value=default_value,
                key=f"state_{category.name}",
                help=category.description
            )
            display_value = f"{value}%"
            st.caption(f"🎯 {value}%")

        elif category.type == "scale_1_10":
            # Шкала 1-10 - исправляем парсинг
            try:
                if current_value:
                    # Извлекаем число из строки "5/10" или "7"
                    if '/' in current_value:
                        clean_value = current_value.split('/')[0].strip()
                        # Убираем эмодзи если есть
                        clean_value = ''.join(c for c in clean_value if c.isdigit())
                        default_value = int(clean_value) if clean_value and 1 <= int(clean_value) <= 10 else 5
                    elif current_value.isdigit():
                        default_value = int(current_value)
                    else:
                        default_value = 5
                else:
                    default_value = 5
            except (ValueError, AttributeError):
                default_value = 5

            value = st.select_slider(
                f"Оценка {category.name.lower()}",
                options=list(range(1, 11)),
                value=default_value,
                key=f"state_{category.name}",
                help=category.description
            )
            # Визуальная шкала
            emoji_scale = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            display_value = f"{emoji_scale[value - 1]} {value}/10"
            st.caption(display_value)

        elif category.type == "text":
            # Текстовый ввод
            value = st.text_input(
                f"Описание {category.name.lower()}",
                value=current_value,
                key=f"state_{category.name}",
                placeholder="Опишите состояние...",
                help=category.description
            )
            display_value = value

        elif category.type == "yes_no":
            # Да/Нет
            options = ["✅ Да", "❌ Нет"]
            default_index = 0 if current_value == "✅ Да" else 1
            value = st.radio(
                f"{category.name}",
                options,
                index=default_index,
                key=f"state_{category.name}",
                horizontal=True,
                help=category.description
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

    @staticmethod
    def render_category_management() -> None:
        """UI для управления категориями состояния"""
        from services.state_service import state_service

        st.subheader("⚙️ Управление категориями состояния")

        # Загружаем текущие категории
        categories = state_service.load_categories()

        # Переключатель режимов
        management_mode = st.radio(
            "Режим управления:",
            ["📋 Просмотр и редактирование", "➕ Добавить новую категорию", "📥 Быстрое добавление"],
            horizontal=True,
            key="category_management_mode_main"  # ИЗМЕНИЛИ
        )

        if management_mode == "📋 Просмотр и редактирование":
            StateComponents._render_category_list(categories, state_service)
        elif management_mode == "➕ Добавить новую категорию":
            StateComponents._render_add_category_form(state_service)
        else:
            StateComponents._render_quick_add_categories(state_service)

    @staticmethod
    def _render_category_list(categories: List[StateCategory], state_service) -> None:
        """Рендеринг списка категорий для редактирования"""

        if not categories:
            st.info("📝 Категории не настроены. Добавьте первую категорию!")
            return

        st.markdown("#### Существующие категории:")

        for i, category in enumerate(categories):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])

                with col1:
                    st.markdown(f"**{i + 1}.**")

                with col2:
                    st.markdown(f"{category.emoji} **{category.name}**")
                    if category.description:
                        st.caption(category.description)

                with col3:
                    type_display = {
                        "percent": "📊 Проценты",
                        "scale_1_10": "🔢 Шкала 1-10",
                        "text": "📝 Текст",
                        "yes_no": "✅ Да/Нет"
                    }
                    st.write(type_display.get(category.type, category.type))

                with col4:
                    # Кнопка редактирования
                    if st.button("✏️ Редактировать", key=f"edit_{category.name}", use_container_width=True):
                        st.session_state[f'editing_{category.name}'] = True

                with col5:
                    # Кнопка удаления (только для пользовательских категорий)
                    is_default = hasattr(category, 'is_default') and category.is_default
                    if not is_default and st.button("🗑️ Удалить", key=f"delete_{category.name}",
                                                    use_container_width=True):
                        try:
                            state_service.delete_category(category.name)
                            st.success(f"Категория '{category.name}' удалена!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка удаления: {e}")

                # Форма редактирования
                if st.session_state.get(f'editing_{category.name}', False):
                    StateComponents._render_edit_category_form(category, state_service)

    @staticmethod
    def _render_edit_category_form(category: StateCategory, state_service) -> None:
        """Форма редактирования категории"""

        st.markdown("---")
        st.markdown(f"##### ✏️ Редактирование: {category.name}")

        with st.form(key=f"edit_form_{category.name}"):
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input("Название", value=category.name)
                new_emoji = st.text_input("Эмодзи", value=category.emoji)
                new_color = st.color_picker("Цвет", value=category.color)

            with col2:
                new_type = st.selectbox(
                    "Тип ввода",
                    state_service.get_category_types(),
                    index=state_service.get_category_types().index(category.type)
                )
                new_description = st.text_area(
                    "Описание",
                    value=category.description,
                    placeholder="Описание категории..."
                )
                new_order = st.number_input(
                    "Порядок отображения",
                    min_value=1,
                    value=category.order
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Сохранить изменения", use_container_width=True):
                    try:
                        updated_category = StateCategory(
                            name=new_name,
                            type=new_type,
                            emoji=new_emoji,
                            color=new_color,
                            description=new_description,
                            order=new_order
                        )
                        state_service.update_category(category.name, updated_category)
                        st.session_state[f'editing_{category.name}'] = False
                        st.success("✅ Категория обновлена!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка обновления: {e}")

            with col2:
                if st.form_submit_button("❌ Отмена", use_container_width=True):
                    st.session_state[f'editing_{category.name}'] = False
                    st.rerun()

    @staticmethod
    def render_category_management() -> None:
        """UI для управления категориями состояния"""
        from services.state_service import state_service

        st.subheader("⚙️ Управление категориями состояния")

        # Загружаем текущие категории
        categories = state_service.load_categories()

        # Переключатель режимов
        management_mode = st.radio(
            "Режим управления:",
            ["📋 Просмотр и редактирование", "➕ Добавить новую категорию", "📥 Быстрое добавление"],
            horizontal=True,
            key="category_management_mode"
        )

        if management_mode == "📋 Просмотр и редактирование":
            StateComponents._render_category_list(categories, state_service)
        elif management_mode == "➕ Добавить новую категорию":
            StateComponents._render_add_category_form(state_service)
        else:
            StateComponents._render_quick_add_categories(state_service)

    @staticmethod
    def _render_add_category_form(state_service) -> None:
        """Форма добавления новой категории"""

        st.markdown("#### Добавить новую категорию")

        with st.form(key="add_category_form_main"):  # ИЗМЕНИЛИ
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input("Название категории *", placeholder="Например: Энергия")
                new_emoji = st.text_input("Эмодзи *", value="⚪", placeholder="⚡")
                new_color = st.color_picker("Цвет *", value="#808080")

            with col2:
                new_type = st.selectbox(
                    "Тип ввода *",
                    state_service.get_category_types()
                )
                new_description = st.text_area(
                    "Описание",
                    placeholder="Краткое описание категории..."
                )
                new_order = st.number_input(
                    "Порядок отображения",
                    min_value=1,
                    value=99
                )

            if st.form_submit_button("➕ Добавить категорию", use_container_width=True):
                if not new_name or not new_emoji:
                    st.error("❌ Заполните обязательные поля (отмечены *)")
                else:
                    try:
                        new_category = StateCategory(
                            name=new_name.strip(),
                            type=new_type,
                            emoji=new_emoji.strip(),
                            color=new_color,
                            description=new_description.strip(),
                            order=new_order
                        )
                        state_service.add_category(new_category)
                        st.success(f"✅ Категория '{new_name}' добавлена!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка добавления: {e}")

    @staticmethod
    def _render_quick_add_categories(state_service) -> None:
        """Быстрое добавление категорий из предустановленного списка"""

        st.markdown("#### 📥 Быстрое добавление категорий")
        st.info("Выберите категории из предустановленного списка для быстрого добавления")

        # Загружаем дополнительные категории
        additional_categories = state_service.load_additional_categories()
        current_categories = state_service.load_categories()

        # Исключаем уже добавленные категории
        current_category_names = {cat.name for cat in current_categories}
        available_categories = [cat for cat in additional_categories if cat.name not in current_category_names]

        if not available_categories:
            st.success("🎉 Все доступные категории уже добавлены!")
            return

        # Показываем категории для быстрого добавления
        for category in available_categories:
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"**{category.emoji} {category.name}**")
                st.caption(category.description)

            with col2:
                type_display = {
                    "percent": "📊 Проценты",
                    "scale_1_10": "🔢 Шкала 1-10",
                    "text": "📝 Текст",
                    "yes_no": "✅ Да/Нет"
                }
                st.write(type_display.get(category.type, category.type))

            with col3:
                if st.button("➕ Добавить", key=f"quick_add_{category.name}", use_container_width=True):
                    try:
                        state_service.add_category(category)
                        st.success(f"✅ Категория '{category.name}' добавлена!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка добавления: {e}")