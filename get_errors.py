import ast
import sys
from pathlib import Path


def check_file_syntax(file_path):
    """Проверяет синтаксис файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        ast.parse(source_code)
        return True, None
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка: {e}"
    except Exception as e:
        return False, f"Ошибка чтения: {e}"


def check_imports():
    """Проверяет основные импорты"""
    imports_to_check = [
        ("services.file_service", "file_service"),
        ("services.diary_service", "diary_service"),
        ("services.project_service", "project_service"),
        ("models.diary", "Day"),
        ("models.diary", "Task"),
        ("models.diary", "DayState"),
        ("models.projects", "Project"),
        ("ui.diary_tab", "diary_tab"),
        ("ui.projects_tab", "projects_tab")
    ]

    errors = []
    for module, obj in imports_to_check:
        try:
            exec(f"from {module} import {obj}")
            print(f"✅ {module}.{obj}")
        except Exception as e:
            errors.append(f"❌ {module}.{obj}: {e}")
            print(f"❌ {module}.{obj}: {e}")

    return errors


if __name__ == "__main__":
    print("🔍 Проверка синтаксиса файлов...")

    # Проверить все .py файлы
    py_files = list(Path('.').rglob('*.py'))

    all_errors = []
    for file in py_files:
        if file.name == 'check_errors.py':
            continue

        is_ok, error = check_file_syntax(file)
        if not is_ok:
            all_errors.append(f"{file}: {error}")
            print(f"❌ {file}: {error}")
        else:
            print(f"✅ {file}")

    print("\n🔍 Проверка импортов...")
    import_errors = check_imports()
    all_errors.extend(import_errors)

    if all_errors:
        print(f"\n🚨 Найдено {len(all_errors)} ошибок:")
        for error in all_errors:
            print(f"  {error}")
    else:
        print("\n🎉 Все проверки пройдены!")