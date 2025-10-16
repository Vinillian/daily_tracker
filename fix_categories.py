import json
from pathlib import Path
from core.constants import CATEGORIES


def fix_categories_in_file(file_path: Path):
    """Исправить категории в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        changed = False
        for period in ['Утро', 'День', 'Вечер']:
            if period in data:
                for task in data[period]:
                    if 'категория' in task:
                        original = task['категория']
                        # Нормализуем категорию
                        if original not in CATEGORIES:
                            # Находим похожую категорию
                            for cat in CATEGORIES:
                                if cat.strip() == original.strip():
                                    task['категория'] = cat
                                    changed = True
                                    print(f"Исправлено: '{original}' -> '{cat}'")
                                    break

        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Файл исправлен: {file_path}")

    except Exception as e:
        print(f"Ошибка в {file_path}: {e}")


def main():
    """Основная функция"""
    data_dir = Path("data/diary")
    for file_path in data_dir.glob("*.json"):
        print(f"Обработка: {file_path.name}")
        fix_categories_in_file(file_path)


if __name__ == "__main__":
    main()