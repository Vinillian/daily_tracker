from typing import List, Dict, Optional
from pydantic import Field, validator
from .base import SerializableModel


class ProjectTask(SerializableModel):
    """Модель задачи проекта"""
    название: str = Field(..., description="Название задачи")
    прогресс: int = Field(0, ge=0, le=100, description="Прогресс выполнения")

    @validator('название')
    def validate_task_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()


class ProjectSection(SerializableModel):
    """Модель секции проекта"""
    название: str = Field(..., description="Название секции")
    задачи: List[ProjectTask] = Field(default_factory=list, description="Задачи секции")

    def calculate_section_progress(self) -> int:
        """Рассчитать прогресс секции"""
        if not self.задачи:
            return 0
        total = sum(task.прогресс for task in self.задачи)
        return total // len(self.задачи)


class ProjectMetadata(SerializableModel):
    """Метаданные проекта"""
    название: str = Field(..., description="Название проекта")
    версия: str = Field("v1.0.0", description="Версия проекта")
    дата: str = Field("{{дата}}", description="Дата создания")
    описание: str = Field("", description="Описание проекта")


class ProjectOverall(SerializableModel):
    """Общая статистика проекта"""
    глобальный_прогресс: int = Field(0, ge=0, le=100, alias="GLOBAL_PROGRESS")
    индекс_стабильности: int = Field(0, ge=0, le=100, alias="STABILITY_INDEX")
    прирост_производительности: int = Field(0, alias="PERFORMANCE_BOOST")
    мобильная_готовность: bool = Field(False, alias="MOBILE_READY")
    веб_режим: str = Field("⚠️ In Development", alias="WEB_MODE")


class Project(SerializableModel):
    """Модель проекта"""
    metadata: ProjectMetadata = Field(..., alias="metadata")
    sections: List[ProjectSection] = Field(default_factory=list, alias="sections")
    overall: ProjectOverall = Field(default_factory=ProjectOverall, alias="overall")

    def calculate_overall_progress(self) -> int:
        """Рассчитать общий прогресс проекта"""
        if not self.sections:
            return 0

        total_tasks = 0
        total_progress = 0

        for section in self.sections:
            for task in section.задачи:
                total_tasks += 1
                total_progress += task.прогресс

        return total_progress // total_tasks if total_tasks > 0 else 0