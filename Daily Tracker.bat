@echo off 
chcp 65001 
call "C:\Users\user\PycharmProjects\daily_tracker\daily_tracker_env\Scripts\activate.bat" 
python -m streamlit run "C:\Users\user\PycharmProjects\daily_tracker\app.py" --server.port 8501 
pause 
