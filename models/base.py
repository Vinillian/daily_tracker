from typing import Any, Dict
from pydantic import BaseModel, validator
import json


class BaseModelConfig(BaseModel):
    """Базовая модель с настройками"""

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        json_encoders = {
            # Добавьте кастомные энкодеры если нужно
        }


class SerializableModel(BaseModelConfig):
    """Модель с методами сериализации"""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        return self.dict(by_alias=True)

    def to_json(self) -> str:
        """Конвертация в JSON строку"""
        return self.json(ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Создание из словаря"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        """Создание из JSON строки"""
        data = json.loads(json_str)
        return cls(**data)