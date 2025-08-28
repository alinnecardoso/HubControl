@echo off
echo ====================================
echo  HubControl - Starting Frontend
echo ====================================

cd frontend

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js nao encontrado. Execute setup_environment.bat primeiro.
    pause
    exit /b 1
)

echo [INFO] Iniciando servidor frontend...
echo [INFO] Aplicacao disponivel em: http://localhost:3000
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.

npm start