import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml


class Config:
    """Конфигурация приложения"""

    def __init__(self):
        # Определяем путь к конфигу относительно exe или скрипта
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent.parent

        self.config_dir = base_dir / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.config_path = self.config_dir / "config.yaml"
        self._data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из YAML"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {
            'save_path': "~/DailyTracker/",
            'reminders': ["08:00", "22:00"],
            'template': "template.md"
        }

    @property
    def save_path(self) -> Path:
        return Path(self._data.get('save_path', "~/DailyTracker/")).expanduser()

    @property
    def reminders(self) -> List[str]:
        return self._data.get('reminders', ["08:00", "22:00"])

    @property
    def template(self) -> str:
        return self._data.get('template', "template.md")


# Глобальный экземпляр конфигурации
config = Config()