from typing import List, Dict
from pydantic import Field, validator
from .base import SerializableModel
from models.state import DayState


class Task(SerializableModel):
    """Task model"""
    task: str = Field(..., description="Название задачи", alias="задача")
    time: str = Field(..., description="Временной интервал", alias="время")
    status: str = Field("☐", description="Статус выполнения", alias="статус")
    progress: int = Field(0, ge=0, le=100, description="Прогресс выполнения (0-100)", alias="прогресс")
    category: str = Field("🏠 Быт", description="Категория задачи", alias="категория")

    @validator('task')
    def validate_task_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()

    @validator('progress')
    def validate_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Прогресс должен быть от 0 до 100')
        return v


class Day(SerializableModel):
    """Day model"""
    morning: List[Task] = Field(default_factory=list, alias="Утро")
    day: List[Task] = Field(default_factory=list, alias="День")
    evening: List[Task] = Field(default_factory=list, alias="Вечер")
    state: DayState = Field(default_factory=DayState, alias="Состояние")  # Английское имя + alias
    notes: List[str] = Field(default_factory=list, alias="Заметки")  # Английское имя + alias

    def get_tasks_by_period(self, period: str) -> List[Task]:
        """Get tasks by day period"""
        period_map = {
            "Утро": self.morning,
            "День": self.day,
            "Вечер": self.evening
        }
        return period_map.get(period, [])

    def add_task(self, period: str, task: Task) -> None:
        """Add task to period"""
        if period == "Утро":
            self.morning.append(task)
        elif period == "День":
            self.day.append(task)
        elif period == "Вечер":
            self.evening.append(task)
        else:
            raise ValueError(f"Unknown period: {period}")

    def calculate_category_progress(self) -> Dict[str, int]:
        """Calculate progress by categories"""
        category_progress = {}

        for period in [self.morning, self.day, self.evening]:
            for task in period:
                if task.category not in category_progress:
                    category_progress[task.category] = []
                category_progress[task.category].append(task.progress)

        return {
            cat: round(sum(progress) / len(progress))
            for cat, progress in category_progress.items() if progress
        }