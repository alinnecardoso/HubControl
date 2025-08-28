@echo off
echo ====================================
echo  HubControl - Running ML Tests
echo ====================================

cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nao encontrado. Execute setup_environment.bat primeiro.
    pause
    exit /b 1
)

echo [INFO] Executando testes do sistema ML...
echo.

python test_ml_system.py

echo.
echo [INFO] Testes concluidos!
pause