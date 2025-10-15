import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, List  # ⬅️ ДОБАВЬТЕ List здесь
from core.exceptions import FileOperationError, DataValidationError
from core.validators import Validators


class FileService:
    """Сервис для работы с файлами"""

    def __init__(self):
        self.encoding = "utf-8"

    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """Загрузка JSON файла с обработкой ошибок"""
        try:
            if not file_path.exists():
                return {}

            content = file_path.read_text(encoding=self.encoding).strip()
            if not content:
                return {}

            return json.loads(content)
        except json.JSONDecodeError as e:
            raise FileOperationError(f"Ошибка парсинга JSON в файле {file_path}: {e}")
        except Exception as e:
            raise FileOperationError(f"Ошибка чтения файла {file_path}: {e}")

    def save_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Сохранение данных в JSON файл"""
        try:
            # Создаем директорию если не существует
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Сохраняем с красивым форматированием
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            file_path.write_text(json_str, encoding=self.encoding)

        except Exception as e:
            raise FileOperationError(f"Ошибка сохранения файла {file_path}: {e}")

    def copy_template(self, template_path: Path, target_path: Path) -> None:
        """Копирование шаблона"""
        try:
            if not template_path.exists():
                raise FileOperationError(f"Шаблон не найден: {template_path}")

            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template_path, target_path)

        except Exception as e:
            raise FileOperationError(f"Ошибка копирования шаблона: {e}")

    def ensure_dir(self, path: Path) -> None:
        """Создание директории если не существует"""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileOperationError(f"Ошибка создания директории {path}: {e}")

    def list_files(self, directory: Path, pattern: str = "*.json") -> List[Path]:
        """Список файлов в директории"""
        try:
            if not directory.exists():
                return []
            return sorted(directory.glob(pattern))
        except Exception as e:
            raise FileOperationError(f"Ошибка чтения директории {directory}: {e}")


# Глобальный экземпляр сервиса
file_service = FileService()