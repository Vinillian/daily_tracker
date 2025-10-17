@echo off
chcp 65001
setlocal enabledelayedexpansion

echo 📦 Установка Daily Tracker (рабочая версия)
echo.

set "INSTALL_DIR=C:\DailyTracker"

echo 🛠 Создаем папку установки...
mkdir "%INSTALL_DIR%" 2>nul
if errorlevel 1 (
    echo ❌ Не удалось создать папку: !INSTALL_DIR!
    echo 💡 Возможно, нужны права администратора
    pause
    exit /b 1
)
echo ✅ Папка создана: !INSTALL_DIR!

echo.
echo 📂 Копируем файлы программы...
echo 📄 Копируем app.py...
copy "app.py" "%INSTALL_DIR%\app.py" >nul
echo ✅ app.py скопирован

echo 📄 Копируем requirements.txt...
copy "requirements.txt" "%INSTALL_DIR%\requirements.txt" >nul
echo ✅ requirements.txt скопирован

echo.
echo 📁 Копируем папки...
for %%F in (core models services ui templates) do (
    if exist "%%F" (
        echo 📁 Копируем %%F...
        echo D | xcopy "%%F" "%INSTALL_DIR%\%%F" /E /Y /Q >nul
        if !errorlevel!==0 (
            echo ✅ %%F скопирован
        ) else (
            echo ❌ Ошибка копирования %%F
        )
    )
)

echo.
echo 📁 Создаем папки данных...
mkdir "%INSTALL_DIR%\data" 2>nul
mkdir "%INSTALL_DIR%\data\diary" 2>nul
mkdir "%INSTALL_DIR%\data\projects" 2>nul
mkdir "%INSTALL_DIR%\config" 2>nul
echo ✅ Папки данных созданы

echo.
echo 🐍 Создаем виртуальное окружение...
echo ⏳ Создаем виртуальное окружение (может занять время)...
python -m venv "%INSTALL_DIR%\venv" >nul 2>&1
if !errorlevel!==0 (
    echo ✅ Виртуальное окружение создано
) else (
    echo ❌ Ошибка создания виртуального окружения
    echo 💡 Проверьте что Python установлен и добавлен в PATH
    pause
    exit /b 1
)

echo.
echo 📦 Устанавливаем зависимости...
echo ⏳ Это может занять несколько минут...
call "%INSTALL_DIR%\venv\Scripts\activate.bat"

echo 🔹 Устанавливаем streamlit...
pip install streamlit --quiet
if !errorlevel!==0 (
    echo ✅ streamlit установлен
) else (
    echo ❌ Ошибка установки streamlit
)

echo 🔹 Устанавливаем PyYAML...
pip install PyYAML --quiet
if !errorlevel!==0 (
    echo ✅ PyYAML установлен
) else (
    echo ❌ Ошибка установки PyYAML
)

echo 🔹 Устанавливаем pydantic...
pip install pydantic --quiet
if !errorlevel!==0 (
    echo ✅ pydantic установлен
) else (
    echo ❌ Ошибка установки pydantic
)

echo.
echo 🔗 Создаем рабочий VBS запускатель...
echo Set WshShell = CreateObject("WScript.Shell") > "%INSTALL_DIR%\Daily Tracker.vbs"
echo WshShell.CurrentDirectory = "%INSTALL_DIR%" >> "%INSTALL_DIR%\Daily Tracker.vbs"
echo WshShell.Run "cmd.exe /c ""venv\Scripts\activate.bat && python -m streamlit run app.py --server.port 8501""", 0, False >> "%INSTALL_DIR%\Daily Tracker.vbs"
echo ✅ VBS запускатель создан

echo 🔗 Создаем ярлык на рабочем столе...
set "DESKTOP=%USERPROFILE%\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo sLinkFile = "%DESKTOP%\Daily Tracker.lnk" >> "%TEMP%\create_shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\create_shortcut.vbs"
echo oLink.TargetPath = "%INSTALL_DIR%\Daily Tracker.vbs" >> "%TEMP%\create_shortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Description = "Daily Tracker - Ежедневник и управление проектами" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Save >> "%TEMP%\create_shortcut.vbs"
cscript //nologo "%TEMP%\create_shortcut.vbs" >nul
del "%TEMP%\create_shortcut.vbs" >nul
echo ✅ Ярлык создан на рабочем столе

:: Файл удаления
echo 📄 Создаем файл удаления...
echo @echo off > "%INSTALL_DIR%\Uninstall.bat"
echo chcp 65001 >> "%INSTALL_DIR%\Uninstall.bat"
echo echo 🗑️ Удаление Daily Tracker... >> "%INSTALL_DIR%\Uninstall.bat"
echo set /p "CONFIRM=Вы уверены? (y/N): " >> "%INSTALL_DIR%\Uninstall.bat"
echo if /i "!CONFIRM!"=="y" ( >> "%INSTALL_DIR%\Uninstall.bat"
echo   echo Удаляем ярлык... >> "%INSTALL_DIR%\Uninstall.bat"
echo   del "%DESKTOP%\Daily Tracker.lnk" 2^>nul >> "%INSTALL_DIR%\Uninstall.bat"
echo   echo Удаляем папку установки... >> "%INSTALL_DIR%\Uninstall.bat"
echo   timeout /t 3 /nobreak ^>nul >> "%INSTALL_DIR%\Uninstall.bat"
echo   rmdir /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\Uninstall.bat"
echo   echo ✅ Удаление завершено! >> "%INSTALL_DIR%\Uninstall.bat"
echo ) else ( >> "%INSTALL_DIR%\Uninstall.bat"
echo   echo ❌ Удаление отменено >> "%INSTALL_DIR%\Uninstall.bat"
echo ) >> "%INSTALL_DIR%\Uninstall.bat"
echo pause >> "%INSTALL_DIR%\Uninstall.bat"
echo ✅ Файл удаления создан


echo.
echo 🎉 УСТАНОВКА ЗАВЕРШЕНА!
echo.
echo 📍 Папка установки: %INSTALL_DIR%
echo 🚀 Запуск: Ярлык "Daily Tracker" на рабочем столе
echo 💡 Особенность: Запускается без командной строки
echo 🗑️ Удаление: Запустите "Uninstall.bat"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul