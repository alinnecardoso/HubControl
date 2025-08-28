@echo off
echo ====================================
echo  HubControl - Starting Backend
echo ====================================

cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nao encontrado. Execute setup_environment.bat primeiro.
    pause
    exit /b 1
)

echo [INFO] Criando diretorio de logs...
mkdir backend\logs 2>nul

echo [INFO] Iniciando servidor backend na porta 8000...
echo [INFO] API disponivel em: http://localhost:8000
echo [INFO] Documentacao em: http://localhost:8000/docs
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000