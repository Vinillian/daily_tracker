from pathlib import Path
from typing import List, Dict, Optional
from datetime import date, timedelta
from core.exceptions import DayNotFoundError, DataValidationError, FileOperationError
from core.constants import DIARY_DIR, TEMPLATE_DIR
from core.validators import Validators
from models.diary import Day, Task, DayState
from services.file_service import file_service


class DiaryService:
    """Сервис для работы с днями"""

    def __init__(self):
        self.data_dir = DIARY_DIR
        self.template_dir = TEMPLATE_DIR
        file_service.ensure_dir(self.data_dir)

    def load_day(self, day_date: str) -> Day:
        """Загрузка дня по дате"""
        day_file = self.data_dir / f"{day_date}.json"

        if not day_file.exists():
            raise DayNotFoundError(f"День {day_date} не найден")

        try:
            data = file_service.load_json(day_file)
            return self._migrate_old_format(data, day_date)
        except Exception as e:
            raise FileOperationError(f"Ошибка загрузки дня {day_date}: {e}")

    def save_day(self, day_date: str, day_data: Day) -> None:
        """Сохранение дня"""
        try:
            Validators.validate_date_format(day_date)
            day_file = self.data_dir / f"{day_date}.json"
            file_service.save_json(day_file, day_data.dict(by_alias=True))
        except DataValidationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Ошибка сохранения дня {day_date}: {e}")

    def create_day(self, day_date: str, template_name: Optional[str] = None) -> Day:
        """Создание нового дня"""
        try:
            Validators.validate_date_format(day_date)

            if template_name:
                return self._create_from_template(day_date, template_name)
            else:
                return Day()

        except DataValidationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Ошибка создания дня {day_date}: {e}")

    def day_exists(self, day_date: str) -> bool:
        """Проверка существования дня"""
        day_file = self.data_dir / f"{day_date}.json"
        return day_file.exists()

    def list_days(self) -> List[str]:
        """Список всех дней"""
        files = file_service.list_files(self.data_dir, "*.json")
        return sorted([f.stem for f in files], reverse=True)

    def copy_day(self, source_date: str, target_date: str) -> None:
        """Копирование дня"""
        try:
            source_day = self.load_day(source_date)

            # Сбрасываем прогресс у задач
            for period in [source_day.утро, source_day.день, source_day.вечер]:
                for task in period:
                    task.прогресс = 0
                    task.статус = "☐"

            # Сбрасываем состояние и заметки
            source_day.состояние = DayState()
            source_day.заметки = []

            self.save_day(target_date, source_day)

        except Exception as e:
            raise FileOperationError(f"Ошибка копирования дня: {e}")

    def _create_from_template(self, day_date: str, template_name: str) -> Day:
        """Создание дня из шаблона"""
        template_file = self.template_dir / f"{template_name}.json"

        if not template_file.exists():
            raise FileOperationError(f"Шаблон {template_name} не найден")

        template_data = file_service.load_json(template_file)
        return self._migrate_old_format(template_data, day_date)

    def _migrate_old_format(self, data: Dict, day_date: str) -> Day:
        """Миграция старых форматов данных"""
        try:
            # Обеспечиваем наличие всех основных полей
            migrated_data = {
                "Утро": data.get("Утро", []),
                "День": data.get("День", []),
                "Вечер": data.get("Вечер", []),
                "Состояние": data.get("Состояние", {}),
                "Заметки": data.get("Заметки", [])
            }

            # Миграция: добавляем категории к старым задачам
            for period in ["Утро", "День", "Вечер"]:
                if period in migrated_data and isinstance(migrated_data[period], list):
                    for task_data in migrated_data[period]:
                        if isinstance(task_data, dict) and "категория" not in task_data:
                            task_data["категория"] = self._suggest_category(task_data.get("задача", ""))

            return Day(**migrated_data)

        except Exception as e:
            raise DataValidationError(f"Ошибка миграции данных дня {day_date}: {e}")

    def _suggest_category(self, task_text: str) -> str:
        """Предложить категорию по тексту задачи"""
        from core.constants import AUTO_CATEGORIES

        if not task_text:
            return "🏠 Быт"

        task_lower = task_text.lower()

        for cat_name, keywords in AUTO_CATEGORIES.items():
            if any(keyword in task_lower for keyword in keywords):
                return cat_name

        return "🏠 Быт"


# Глобальный экземпляр сервиса
diary_service = DiaryService()