from typing import List, Dict, Optional
from pydantic import Field, validator
from .base import SerializableModel
from core.validators import Validators


class Task(SerializableModel):
    """Модель задачи"""
    задача: str = Field(..., description="Название задачи")
    время: str = Field(..., description="Временной интервал")
    статус: str = Field("☐", description="Статус выполнения")
    прогресс: int = Field(0, ge=0, le=100, description="Прогресс выполнения (0-100)")
    категория: str = Field("🏠 Быт", description="Категория задачи")

    @validator('задача')
    def validate_task_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()

    @validator('прогресс')
    def validate_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Прогресс должен быть от 0 до 100')
        return v


class DayState(SerializableModel):
    """Модель состояния дня"""
    тело: str = Field("", alias="💪 Тело")
    энергия: str = Field("", alias="🧘 Энергия")
    пищеварение: str = Field("", alias="💨 Пищеварение")
    концентрация: str = Field("", alias="🧠 Концентрация")
    настроение: str = Field("", alias="🌿 Настроение")
    фактор_погоды: str = Field("", alias="🌦️ Фактор погоды")


class Day(SerializableModel):
    """Модель дня"""
    утро: List[Task] = Field(default_factory=list, alias="Утро")
    день: List[Task] = Field(default_factory=list, alias="День")
    вечер: List[Task] = Field(default_factory=list, alias="Вечер")
    состояние: DayState = Field(default_factory=DayState, alias="Состояние")
    заметки: List[str] = Field(default_factory=list, alias="Заметки")

    def get_tasks_by_period(self, period: str) -> List[Task]:
        """Получить задачи по периоду дня"""
        period_map = {
            "Утро": self.утро,
            "День": self.день,
            "Вечер": self.вечер
        }
        return period_map.get(period, [])

    def add_task(self, period: str, task: Task) -> None:
        """Добавить задачу в период"""
        if period == "Утро":
            self.утро.append(task)
        elif period == "День":
            self.день.append(task)
        elif period == "Вечер":
            self.вечер.append(task)
        else:
            raise ValueError(f"Неизвестный период: {period}")

    def calculate_category_progress(self) -> Dict[str, int]:
        """Рассчитать прогресс по категориям"""
        category_progress = {}

        for period in [self.утро, self.день, self.вечер]:
            for task in period:
                if task.категория not in category_progress:
                    category_progress[task.категория] = []
                category_progress[task.категория].append(task.прогресс)

        return {
            cat: round(sum(progress) / len(progress))
            for cat, progress in category_progress.items() if progress
        }