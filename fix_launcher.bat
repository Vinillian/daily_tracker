@echo off
chcp 65001

echo 🔧 Исправление запуска Daily Tracker...
echo.

set "INSTALL_DIR=C:\DailyTracker"

echo 📄 Создаем новый VBS запускатель...
echo Set WshShell = CreateObject("WScript.Shell") > "%INSTALL_DIR%\Start Daily Tracker.vbs"
echo WshShell.CurrentDirectory = "%INSTALL_DIR%" >> "%INSTALL_DIR%\Start Daily Tracker.vbs"
echo WshShell.Run "cmd.exe /c ""venv\Scripts\activate.bat && python -m streamlit run app.py --server.port 8501""", 0, False >> "%INSTALL_DIR%\Start Daily Tracker.vbs"

echo 🔗 Создаем ярлык...
set "DESKTOP=%USERPROFILE%\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\new_shortcut.vbs"
echo sLinkFile = "%DESKTOP%\Daily Tracker.lnk" >> "%TEMP%\new_shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\new_shortcut.vbs"
echo oLink.TargetPath = "%INSTALL_DIR%\Start Daily Tracker.vbs" >> "%TEMP%\new_shortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\new_shortcut.vbs"
echo oLink.Description = "Daily Tracker" >> "%TEMP%\new_shortcut.vbs"
echo oLink.Save >> "%TEMP%\new_shortcut.vbs"
cscript //nologo "%TEMP%\new_shortcut.vbs"
del "%TEMP%\new_shortcut.vbs"

echo.
echo ✅ Исправление завершено!
echo 🚀 Попробуйте новый ярлык на рабочем столе
echo.
pause