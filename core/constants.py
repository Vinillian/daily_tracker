import os
import sys
from pathlib import Path
from typing import List, Dict


# Определяем базовую папку для данных
def get_base_dir():
    """Определяем где хранить данные - в папке пользователя"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe - данные в AppData/Roaming
        base_dir = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "DailyTracker"
    else:
        # Если запущено как скрипт - в папке проекта
        base_dir = Path(__file__).parent.parent

    # Инициализируем приложение (распаковываем шаблоны)
    try:
        from init_app import init_app
        base_dir = init_app()
    except Exception as e:
        print(f"⚠️ Ошибка инициализации: {e}")

    # Создаем необходимые папки
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    diary_dir = data_dir / "diary"
    diary_dir.mkdir(exist_ok=True)

    projects_dir = data_dir / "projects"
    projects_dir.mkdir(exist_ok=True)

    config_dir = base_dir / "config"
    config_dir.mkdir(exist_ok=True)

    return base_dir


BASE_DIR = get_base_dir()

# Пути
DATA_DIR = BASE_DIR / "data"
DIARY_DIR = DATA_DIR / "diary"
PROJECTS_DIR = DATA_DIR / "projects"
TEMPLATE_DIR = BASE_DIR / "templates"
PROJECT_TEMPLATES_DIR = BASE_DIR / "templates" / "project_templates"

# Создаем папки если не существуют
for directory in [DATA_DIR, DIARY_DIR, PROJECTS_DIR, TEMPLATE_DIR, PROJECT_TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Периоды дня
DAY_PERIODS = ["Утро", "День", "Вечер"]
PERIOD_ICONS = {"Утро": "🌅", "День": "🌞", "Вечер": "🌇"}

# Статусы задач
TASK_STATUSES = ["☐", "✅", "☑️", "❌"]
STATUS_EMOJIS = {"☐": "⚪", "✅": "🟢", "☑️": "🟡", "❌": "🔴"}

CATEGORIES = [
    "🩺 Здоровье", "💼 Работа", "📚 Обучение",
    "🧘 Практики", "🏠 Быт", "🎭 Отдых",
    "👥 Общение", "💖 Отношения", "🌱 Развитие",
    "🎨 Творчество", "🏃 Спорт", "🙏 Духовное",
    "💰 Финансы", "🚀 Проекты", "🌍 Путешествия"
]

# Автоматические категории (ключевые слова)
AUTO_CATEGORIES: Dict[str, List[str]] = {
    "🩺 Здоровье": ["🩺", "🚑", "💊", "врач", "больниц", "здоровь", "нейрохирург", "приём", "консультация", "диагностика"],
    "💼 Работа": ["📦", "💼", "🚚", "курьер", "работ", "доход", "зарабат", "проект"],
    "📚 Обучение": ["📚", "🧮", "📖", "python", "изучение", "лекция", "чтение", "марк лутц", "класс", "атрибут",
                   "программирование"],
    "🧘 Практики": ["🕉️", "🧘", "☯️", "медитац", "мантра", "растяжка", "даосизм", "духовн", "практик"],
    "🏠 Быт": ["🏠", "🛏️", "☕", "🍽️", "🛀", "уборк", "завтрак", "ужин", "сбор", "документ", "дом"],
    "🎭 Отдых": ["📺", "🎬", "🚶", "сериал", "отдых", "прогулка", "разговор", "хобби", "развлечен"]
}

# Временные интервалы
TIME_SLOTS = [f"{hour:02d}:{minute:02d}" for hour in range(0, 24) for minute in [0, 15, 30, 45]]
POPULAR_TIME_RANGES = [
    "07:00–08:00", "08:00–09:00", "09:00–10:00", "10:00–11:00",
    "11:00–12:00", "12:00–13:00", "13:00–14:00", "14:00–15:00",
    "15:00–16:00", "16:00–17:00", "17:00–18:00", "18:00–19:00",
    "19:00–20:00", "20:00–21:00", "21:00–22:00", "22:00–23:00"
]