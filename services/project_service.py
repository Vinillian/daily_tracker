from pathlib import Path
from typing import List, Dict, Optional
from core.exceptions import ProjectNotFoundError, DataValidationError, FileOperationError
from core.constants import PROJECTS_DIR, PROJECT_TEMPLATES_DIR
from core.validators import Validators
from models.projects import Project, ProjectMetadata, ProjectSection, ProjectTask, ProjectOverall
from services.file_service import file_service


class ProjectService:
    """Сервис для работы с проектами"""

    def __init__(self):
        self.data_dir = PROJECTS_DIR
        self.template_dir = PROJECT_TEMPLATES_DIR
        file_service.ensure_dir(self.data_dir)

    def load_project(self, project_name: str) -> Project:
        """Загрузка проекта по имени"""
        project_file = self.data_dir / f"{project_name}.json"

        if not project_file.exists():
            raise ProjectNotFoundError(f"Проект {project_name} не найден")

        try:
            data = file_service.load_json(project_file)
            return self._migrate_old_format(data, project_name)
        except Exception as e:
            raise FileOperationError(f"Ошибка загрузки проекта {project_name}: {e}")

    def save_project(self, project_name: str, project_data: Project) -> None:
        """Сохранение проекта"""
        try:
            Validators.validate_filename(project_name)
            project_file = self.data_dir / f"{project_name}.json"
            file_service.save_json(project_file, project_data.dict(by_alias=True))
        except DataValidationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Ошибка сохранения проекта {project_name}: {e}")

    def create_project(self, project_name: str, template_name: Optional[str] = None) -> Project:
        """Создание нового проекта"""
        try:
            Validators.validate_filename(project_name)

            if template_name:
                return self._create_from_template(project_name, template_name)
            else:
                return self._create_empty_project(project_name)

        except DataValidationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Ошибка создания проекта {project_name}: {e}")

    def project_exists(self, project_name: str) -> bool:
        """Проверка существования проекта"""
        project_file = self.data_dir / f"{project_name}.json"
        return project_file.exists()

    def list_projects(self) -> List[str]:
        """Список всех проектов"""
        files = file_service.list_files(self.data_dir, "*.json")
        return sorted([f.stem for f in files], reverse=True)

    def delete_project(self, project_name: str) -> None:
        """Удаление проекта"""
        try:
            project_file = self.data_dir / f"{project_name}.json"
            if project_file.exists():
                project_file.unlink()
        except Exception as e:
            raise FileOperationError(f"Ошибка удаления проекта {project_name}: {e}")

    def _create_from_template(self, project_name: str, template_name: str) -> Project:
        """Создание проекта из шаблона"""
        template_file = self.template_dir / f"{template_name}.json"

        if not template_file.exists():
            raise FileOperationError(f"Шаблон проекта {template_name} не найден")

        template_data = file_service.load_json(template_file)
        migrated_data = self._migrate_old_format(template_data, project_name)

        # Обновляем название в метаданных
        migrated_data.metadata.название = project_name
        return migrated_data

    def _create_empty_project(self, project_name: str) -> Project:
        """Создание пустого проекта"""
        return Project(
            metadata=ProjectMetadata(
                название=project_name,
                версия="v1.0.0",
                дата="{{дата}}",
                описание="Новый проект"
            ),
            sections=[
                ProjectSection(
                    название="📋 Планирование",
                    задачи=[
                        ProjectTask(название="Определение требований", прогресс=0),
                        ProjectTask(название="Проектирование архитектуры", прогресс=0)
                    ]
                )
            ],
            overall=ProjectOverall(
                GLOBAL_PROGRESS=0,
                STABILITY_INDEX=0,
                PERFORMANCE_BOOST=0,
                MOBILE_READY=False,
                WEB_MODE="❌ Not supported"
            )
        )

    def _migrate_old_format(self, data: Dict, project_name: str) -> Project:
        """Миграция старых форматов данных проекта"""
        try:
            # Новый формат с sections
            if "sections" in data or "sections" in data.get("metadata", {}):
                return Project(**data)

            # Старый формат с плоской структурой
            migrated_data = {
                "metadata": data.get("metadata", {
                    "название": project_name,
                    "версия": "v1.0.0",
                    "дата": "{{дата}}",
                    "описание": data.get("metadata", {}).get("описание", "")
                }),
                "sections": [],
                "overall": data.get("overall", {})
            }

            # Конвертируем плоские секции в новый формат
            for key, value in data.items():
                if key not in ["metadata", "overall"] and isinstance(value, dict):
                    tasks = []
                    for task_name, progress in value.items():
                        if isinstance(progress, (int, float)):
                            tasks.append(ProjectTask(название=task_name, прогресс=progress))

                    if tasks:
                        migrated_data["sections"].append(
                            ProjectSection(название=key, задачи=tasks)
                        )

            return Project(**migrated_data)

        except Exception as e:
            raise DataValidationError(f"Ошибка миграции данных проекта {project_name}: {e}")


# Глобальный экземпляр сервиса
project_service = ProjectService()