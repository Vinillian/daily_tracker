import json
from pathlib import Path
import uuid


def migrate_file(file_path: Path):
    """Добавить ID к существующим задачам"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        changed = False
        for period in ['Утро', 'День', 'Вечер']:
            if period in data and isinstance(data[period], list):
                for task in data[period]:
                    if isinstance(task, dict) and 'id' not in task:
                        task['id'] = str(uuid.uuid4())
                        changed = True
                        print(f"  Добавлен ID для задачи: {task.get('задача', 'Unknown')}")

        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Мигрирован: {file_path}")
        else:
            print(f"✓ Уже мигрирован: {file_path}")

    except Exception as e:
        print(f"❌ Ошибка в {file_path}: {e}")


def main():
    """Основная функция миграции"""
    print("🔄 Начинаем миграцию ID задач...")
    data_dir = Path("data/diary")

    if not data_dir.exists():
        print("❌ Директория data/diary не найдена")
        return

    files = list(data_dir.glob("*.json"))
    if not files:
        print("❌ Файлы для миграции не найдены")
        return

    print(f"📁 Найдено файлов: {len(files)}")

    for file_path in files:
        print(f"\n🔧 Обработка: {file_path.name}")
        migrate_file(file_path)

    print(f"\n🎉 Миграция завершена! Обработано файлов: {len(files)}")


if __name__ == "__main__":
    main()