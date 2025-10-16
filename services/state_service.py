from pathlib import Path
from typing import List, Dict, Optional
import yaml
from core.exceptions import FileOperationError
from models.state import StateCategory



class StateService:
    """Сервис для управления категориями состояния"""

    def __init__(self):
        self.config_dir = Path("config")
        self.default_categories_file = self.config_dir / "state_categories.yaml"
        self.user_categories_file = self.config_dir / "user_state_categories.yaml"
        self.additional_categories_file = self.config_dir / "additional_categories.yaml"  # НОВОЕ
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Создать директорию конфигурации если не существует"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            self._create_default_categories()
        except Exception as e:
            raise FileOperationError(f"Ошибка создания директории конфигурации: {e}")

    def load_additional_categories(self) -> List[StateCategory]:
        """Загрузка дополнительных категорий"""
        if not self.additional_categories_file.exists():
            self._create_additional_categories()

        try:
            with open(self.additional_categories_file, 'r', encoding='utf-8') as f:
                additional_data = yaml.safe_load(f) or {}
                additional_categories = additional_data.get('categories', [])
                return [StateCategory(**cat) for cat in additional_categories]
        except Exception as e:
            print(f"Ошибка загрузки дополнительных категорий: {e}")
            return []

    def _create_additional_categories(self) -> None:
        """Создать файл с дополнительными категориями"""
        try:
            self.additional_categories_file.parent.mkdir(parents=True, exist_ok=True)

            additional_categories = [
                {
                    "name": "🍽️ Пищеварение",
                    "type": "text",
                    "emoji": "🍽️",
                    "color": "#00B894",
                    "description": "Состояние пищеварительной системы",
                    "order": 7
                },
                {
                    "name": "💊 Физическое здоровье",
                    "type": "percent",
                    "emoji": "💊",
                    "color": "#FD79A8",
                    "description": "Общее физическое самочувствие",
                    "order": 8
                },
                # ... остальные категории из additional_categories.yaml
                {
                    "name": "⚡ Пиковая производительность",
                    "type": "yes_no",
                    "emoji": "⚡",
                    "color": "#FED330",
                    "description": "Были ли вы сегодня на пике производительности?",
                    "order": 20
                }
            ]

            with open(self.additional_categories_file, 'w', encoding='utf-8') as f:
                yaml.dump({"categories": additional_categories}, f, allow_unicode=True, indent=2)
        except Exception as e:
            raise FileOperationError(f"Ошибка создания дополнительных категорий: {e}")

    def _create_default_categories(self) -> None:
        """Создать файл с категориями по умолчанию"""
        if not self.default_categories_file.exists():
            try:
                # Создаем директорию если не существует
                self.default_categories_file.parent.mkdir(parents=True, exist_ok=True)

                default_categories = [
                    {
                        "name": "💪 Уровень энергии",
                        "type": "percent",
                        "emoji": "💪",
                        "color": "#FF6B6B",
                        "description": "Физическая энергия и жизненный тонус",
                        "order": 1
                    },
                    {
                        "name": "🧠 Ментальная концентрация",
                        "type": "scale_1_10",
                        "emoji": "🧠",
                        "color": "#4ECDC4",
                        "description": "Способность к концентрации и фокусировке",
                        "order": 2
                    },
                    {
                        "name": "😌 Настроение",
                        "type": "scale_1_10",
                        "emoji": "😌",
                        "color": "#FFD93D",
                        "description": "Общее эмоциональное состояние",
                        "order": 3
                    },
                    {
                        "name": "🛌 Качество сна",
                        "type": "scale_1_10",
                        "emoji": "🛌",
                        "color": "#6C5CE7",
                        "description": "Насколько хорошо вы спали прошлой ночью",
                        "order": 4
                    },
                    {
                        "name": "🍽️ Пищеварение",
                        "type": "text",
                        "emoji": "🍽️",
                        "color": "#00B894",
                        "description": "Состояние пищеварительной системы",
                        "order": 5
                    },
                    {
                        "name": "💊 Физическое здоровье",
                        "type": "percent",
                        "emoji": "💊",
                        "color": "#FD79A8",
                        "description": "Общее физическое самочувствие",
                        "order": 6
                    },
                    {
                        "name": "🧘 Уровень стресса",
                        "type": "scale_1_10",
                        "emoji": "🧘",
                        "color": "#E17055",
                        "description": "Текущий уровень стресса и напряжения",
                        "order": 7
                    },
                    {
                        "name": "💭 Ментальная ясность",
                        "type": "scale_1_10",
                        "emoji": "💭",
                        "color": "#74B9FF",
                        "description": "Ясность мышления и умственная острота",
                        "order": 8
                    },
                    {
                        "name": "🏃 Физическая активность",
                        "type": "percent",
                        "emoji": "🏃",
                        "color": "#55E6C1",
                        "description": "Уровень физической активности и упражнений",
                        "order": 9
                    },
                    {
                        "name": "🍎 Питание",
                        "type": "scale_1_10",
                        "emoji": "🍎",
                        "color": "#FF9FF3",
                        "description": "Качество питания и пищевых привычек",
                        "order": 10
                    },
                    {
                        "name": "💧 Гидратация",
                        "type": "percent",
                        "emoji": "💧",
                        "color": "#3867D6",
                        "description": "Потребление воды и уровень гидратации",
                        "order": 11
                    },
                    {
                        "name": "🌞 Утренняя энергия",
                        "type": "percent",
                        "emoji": "🌞",
                        "color": "#FDCB6E",
                        "description": "Уровень энергии при пробуждении",
                        "order": 12
                    },
                    {
                        "name": "🌙 Вечерняя энергия",
                        "type": "percent",
                        "emoji": "🌙",
                        "color": "#A29BFE",
                        "description": "Уровень энергии вечером",
                        "order": 13
                    },
                    {
                        "name": "📚 Фокус на обучении",
                        "type": "scale_1_10",
                        "emoji": "📚",
                        "color": "#00CEC9",
                        "description": "Способность фокусироваться на учебных задачах",
                        "order": 14
                    },
                    {
                        "name": "💼 Продуктивность",
                        "type": "percent",
                        "emoji": "💼",
                        "color": "#636E72",
                        "description": "Продуктивность на работе/учебе",
                        "order": 15
                    },
                    {
                        "name": "👥 Социальная энергия",
                        "type": "scale_1_10",
                        "emoji": "👥",
                        "color": "#F8A5C2",
                        "description": "Энергия для социальных взаимодействий",
                        "order": 16
                    },
                    {
                        "name": "🎯 Мотивация",
                        "type": "scale_1_10",
                        "emoji": "🎯",
                        "color": "#546DE5",
                        "description": "Общая мотивация и драйв",
                        "order": 17
                    },
                    {
                        "name": "🔄 Восстановление",
                        "type": "percent",
                        "emoji": "🔄",
                        "color": "#C44569",
                        "description": "Уровень восстановления тела и ума",
                        "order": 18
                    },
                    {
                        "name": "🌿 Общее благополучие",
                        "type": "scale_1_10",
                        "emoji": "🌿",
                        "color": "#26DE81",
                        "description": "Общее ощущение благополучия",
                        "order": 19
                    },
                    {
                        "name": "⚡ Пиковая производительность",
                        "type": "yes_no",
                        "emoji": "⚡",
                        "color": "#FED330",
                        "description": "Были ли вы сегодня на пике производительности?",
                        "order": 20
                    }
                ]

                with open(self.default_categories_file, 'w', encoding='utf-8') as f:
                    yaml.dump({"categories": default_categories}, f, allow_unicode=True, indent=2)
            except Exception as e:
                raise FileOperationError(f"Ошибка создания категорий по умолчанию: {e}")

    def load_categories(self) -> List[StateCategory]:
        """Загрузка категорий (сначала пользовательские, потом дефолтные)"""
        categories = []

        # Загружаем пользовательские категории если есть
        if self.user_categories_file.exists():
            try:
                with open(self.user_categories_file, 'r', encoding='utf-8') as f:
                    user_data = yaml.safe_load(f) or {}
                    user_categories = user_data.get('categories', [])
                    categories.extend([StateCategory(**cat) for cat in user_categories])
            except Exception as e:
                print(f"Ошибка загрузки пользовательских категорий: {e}")

        # Загружаем дефолтные категории
        try:
            with open(self.default_categories_file, 'r', encoding='utf-8') as f:
                default_data = yaml.safe_load(f) or {}
                default_categories = default_data.get('categories', [])

                # Добавляем только те дефолтные категории, которых нет у пользователя
                user_category_names = {cat.name for cat in categories}
                for cat_data in default_categories:
                    if cat_data['name'] not in user_category_names:
                        categories.append(StateCategory(**cat_data))

        except Exception as e:
            print(f"Ошибка загрузки дефолтных категорий: {e}")

        # Сортируем по порядку
        return sorted(categories, key=lambda x: x.order)

    def add_category(self, category: StateCategory) -> None:
        """Добавление новой категории"""
        try:
            categories = self.load_categories()

            # Проверяем уникальность имени
            if any(cat.name == category.name for cat in categories):
                raise ValueError(f"Категория с именем '{category.name}' уже существует")

            categories.append(category)
            self.save_user_categories(categories)

        except Exception as e:
            raise FileOperationError(f"Ошибка добавления категории: {e}")

    def update_category(self, category_name: str, updated_category: StateCategory) -> None:
        """Обновление существующей категории"""
        try:
            categories = self.load_categories()

            for i, cat in enumerate(categories):
                if cat.name == category_name:
                    categories[i] = updated_category
                    self.save_user_categories(categories)
                    return

            raise ValueError(f"Категория '{category_name}' не найдена")

        except Exception as e:
            raise FileOperationError(f"Ошибка обновления категории: {e}")

    def delete_category(self, category_name: str) -> None:
        """Удаление категории"""
        try:
            categories = self.load_categories()

            # Не позволяем удалять дефолтные категории
            default_categories = self._load_default_categories()
            default_names = {cat.name for cat in default_categories}

            if category_name in default_names:
                raise ValueError("Нельзя удалять категории по умолчанию")

            # Удаляем категорию
            categories = [cat for cat in categories if cat.name != category_name]
            self.save_user_categories(categories)

        except Exception as e:
            raise FileOperationError(f"Ошибка удаления категории: {e}")

    def reorder_categories(self, new_order: List[str]) -> None:
        """Изменение порядка категорий"""
        try:
            categories = self.load_categories()
            category_dict = {cat.name: cat for cat in categories}

            # Создаем новый упорядоченный список
            reordered_categories = []
            for name in new_order:
                if name in category_dict:
                    reordered_categories.append(category_dict[name])

            # Добавляем оставшиеся категории (если есть)
            for cat in categories:
                if cat.name not in new_order:
                    reordered_categories.append(cat)

            # Обновляем порядок
            for i, cat in enumerate(reordered_categories):
                cat.order = i + 1

            self.save_user_categories(reordered_categories)

        except Exception as e:
            raise FileOperationError(f"Ошибка изменения порядка категорий: {e}")

    def _load_default_categories(self) -> List[StateCategory]:
        """Загрузка только дефолтных категорий"""
        try:
            with open(self.default_categories_file, 'r', encoding='utf-8') as f:
                default_data = yaml.safe_load(f) or {}
                default_categories = default_data.get('categories', [])
                return [StateCategory(**cat) for cat in default_categories]
        except Exception:
            return []

    def save_user_categories(self, categories: List[StateCategory]) -> None:
        """Сохранение пользовательских категорий"""
        try:
            # Используем dict() вместо model_dump для совместимости
            data = {"categories": [cat.dict() for cat in categories]}
            with open(self.user_categories_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, indent=2)
        except Exception as e:
            raise FileOperationError(f"Ошибка сохранения пользовательских категорий: {e}")

    @staticmethod
    def get_category_types() -> List[str]:
        """Получить доступные типы категорий"""
        return ["percent", "scale_1_10", "text", "yes_no"]


# Глобальный экземпляр сервиса
state_service = StateService()