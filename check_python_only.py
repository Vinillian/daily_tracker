import subprocess
import sys


def main():
    print("Проверка Python файлов...")

    # Flake8 проверка
    result = subprocess.run([
        'flake8', '.',
        '--exclude=.venv,__pycache__,tests',
        '--filename=*.py',
        '--count',
        '--select=E,W,F'
    ], capture_output=True, text=True)

    print("РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print(result.stdout)

    if result.stderr:
        print("ОШИБКИ:", result.stderr)

    # Сохраняем в файл
    with open('python_errors_detailed.txt', 'w', encoding='utf-8') as f:
        f.write("Ошибки в Python файлах:\n")
        f.write(result.stdout)


if __name__ == "__main__":
    main()