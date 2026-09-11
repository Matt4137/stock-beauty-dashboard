@echo off
title StockVision
cd /d "%~dp0"
echo =============================================
echo         STOCKVISION - INICIANDO APP
echo =============================================
python -m ensurepip --upgrade
python -m pip install -r requirements.txt
python -m streamlit run app.py
echo.
echo Si aparece un error, toma una captura de esta ventana.
pause
