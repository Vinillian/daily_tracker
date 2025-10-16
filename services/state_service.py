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
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Создать директорию конфигурации если не существует"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            self._create_default_categories()
        except Exception as e:
            raise FileOperationError(f"Ошибка создания директории конфигурации: {e}")

    def _create_default_categories(self) -> None:
        """Создать файл с категориями по умолчанию"""
        if not self.default_categories_file.exists():
            default_categories = [
                {
                    "name": "💪 Энергия",
                    "type": "percent",
                    "emoji": "💪",
                    "color": "#FF6B6B",
                    "description": "Уровень физической энергии",
                    "order": 1
                },
                {
                    "name": "🧠 Фокус",
                    "type": "scale_1_10",
                    "emoji": "🧠",
                    "color": "#4ECDC4",
                    "description": "Способность концентрироваться",
                    "order": 2
                },
                {
                    "name": "😌 Настроение",
                    "type": "scale_1_10",
                    "emoji": "😌",
                    "color": "#FFD93D",
                    "description": "Эмоциональное состояние",
                    "order": 3
                },
                {
                    "name": "🛌 Качество сна",
                    "type": "scale_1_10",
                    "emoji": "🛌",
                    "color": "#6C5CE7",
                    "description": "Как вы спали прошлой ночью",
                    "order": 4
                },
                {
                    "name": "🍽️ Пищеварение",
                    "type": "text",
                    "emoji": "🍽️",
                    "color": "#00B894",
                    "description": "Состояние пищеварительной системы",
                    "order": 5
                }
            ]

            try:
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

    def save_user_categories(self, categories: List[StateCategory]) -> None:
        """Сохранение пользовательских категорий"""
        try:
            data = {"categories": [cat.model_dump() for cat in categories]}  # ИСПРАВЛЕНО: model_dump вместо dict
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