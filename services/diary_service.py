from pathlib import Path
from typing import Dict, Optional, List
from core.exceptions import DayNotFoundError, DataValidationError, FileOperationError
from core.constants import DIARY_DIR, TEMPLATE_DIR
from core.validators import Validators
from models.diary import Day, Task
from services.file_service import file_service


class DiaryService:
    """Service for working with days"""

    def __init__(self):
        self.data_dir = DIARY_DIR
        self.template_dir = TEMPLATE_DIR
        file_service.ensure_dir(self.data_dir)

    def load_day(self, day_date: str) -> Day:
        """Load day by date"""
        day_file = self.data_dir / f"{day_date}.json"

        if not day_file.exists():
            raise DayNotFoundError(f"Day {day_date} not found")

        try:
            data = file_service.load_json(day_file)
            return Day(**data)  # Pydantic сам разберется с alias
        except Exception as e:
            raise FileOperationError(f"Error loading day {day_date}: {e}")

    def save_day(self, day_date: str, day_data: Day) -> None:
        """Save day"""
        try:
            Validators.validate_date_format(day_date)
            day_file = self.data_dir / f"{day_date}.json"
            file_service.save_json(day_file, day_data.model_dump(by_alias=True))
        except DataValidationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Error saving day {day_date}: {e}")

    def create_day(self, day_date: str, template_name: Optional[str] = None) -> Day:
        """Create new day"""
        try:
            Validators.validate_date_format(day_date)

            if template_name:
                return self._create_from_template(day_date, template_name)
            else:
                # Создаем действительно пустой день с правильной структурой
                from models.state import DayState
                return Day(
                    morning=[],
                    day=[],
                    evening=[],
                    state=DayState(),
                    notes=[]
                )

        except DataValidationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Error creating day {day_date}: {e}")

    def day_exists(self, day_date: str) -> bool:
        """Check if day exists"""
        day_file = self.data_dir / f"{day_date}.json"
        return day_file.exists()

    def list_days(self) -> List[str]:
        """List all days"""
        files = file_service.list_files(self.data_dir, "*.json")
        return sorted([f.stem for f in files], reverse=True)

    def copy_day(self, source_date: str, target_date: str) -> None:
        """Copy day"""
        try:
            source_day = self.load_day(source_date)

            # Reset progress for tasks
            for period in [source_day.morning, source_day.day, source_day.evening]:
                for task in period:
                    task.progress = 0
                    task.status = "☐"

            # Reset state and notes
            from models.state import DayState
            source_day.state = DayState()
            source_day.notes = []

            self.save_day(target_date, source_day)

        except Exception as e:
            raise FileOperationError(f"Error copying day: {e}")

    def _create_from_template(self, day_date: str, template_name: str) -> Day:
        """Create day from template"""
        template_file = self.template_dir / f"{template_name}.json"

        if not template_file.exists():
            raise FileOperationError(f"Template {template_name} not found")

        try:
            template_data = file_service.load_json(template_file)

            # Заменяем плейсхолдеры в шаблоне
            import uuid
            import json

            # Рекурсивно обходим данные и заменяем плейсхолдеры
            def replace_placeholders(obj):
                if isinstance(obj, dict):
                    return {key: replace_placeholders(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [replace_placeholders(item) for item in obj]
                elif isinstance(obj, str):
                    # Заменяем {{дата}} на актуальную дату
                    if "{{дата}}" in obj:
                        obj = obj.replace("{{дата}}", day_date)
                    # Заменяем {{uuid}} на реальные UUID
                    if "{{uuid}}" in obj:
                        obj = obj.replace("{{uuid}}", str(uuid.uuid4()))
                    return obj
                else:
                    return obj

            processed_data = replace_placeholders(template_data)
            return Day(**processed_data)

        except Exception as e:
            raise FileOperationError(f"Error loading template {template_name}: {e}")

    def _suggest_category(self, task_text: str) -> str:
        """Suggest category by task text"""
        from core.constants import AUTO_CATEGORIES

        if not task_text:
            return "🏠 Быт"

        task_lower = task_text.lower()

        for cat_name, keywords in AUTO_CATEGORIES.items():
            if any(keyword in task_lower for keyword in keywords):
                return cat_name

        return "🏠 Быт"


# Global service instance
diary_service = DiaryService()