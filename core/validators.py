import re
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from .exceptions import DataValidationError


class Validators:
    """Валидаторы данных"""

    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Проверка формата даты YYYY-MM-DD"""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_filename(name: str) -> bool:
        """Проверка безопасного имени файла"""
        if not name or len(name) > 255:
            return False

        # Запрещенные символы в именах файлов
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(char in name for char in forbidden_chars)

    @staticmethod
    def validate_task_data(task_data: Dict[str, Any]) -> None:
        """Валидация данных задачи"""
        required_fields = ['задача', 'время', 'статус', 'прогресс']

        for field in required_fields:
            if field not in task_data:
                raise DataValidationError(f"Отсутствует обязательное поле: {field}")

        if not isinstance(task_data['задача'], str) or not task_data['задача'].strip():
            raise DataValidationError("Название задачи не может быть пустым")

        if not isinstance(task_data['прогресс'], int) or not 0 <= task_data['прогресс'] <= 100:
            raise DataValidationError("Прогресс должен быть числом от 0 до 100")

    @staticmethod
    def validate_project_metadata(metadata: Dict[str, Any]) -> None:
        """Валидация метаданных проекта"""
        required_fields = ['название', 'версия', 'дата']

        for field in required_fields:
            if field not in metadata:
                raise DataValidationError(f"Отсутствует обязательное поле в метаданных: {field}")

        if not isinstance(metadata['название'], str) or not metadata['название'].strip():
            raise DataValidationError("Название проекта не может быть пустым")