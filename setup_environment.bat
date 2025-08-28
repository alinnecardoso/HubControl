@echo off
echo ====================================
echo  HubControl - Setup Environment
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nao encontrado. Instale Python 3.8+ primeiro.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python encontrado, instalando dependencias do backend...
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Falha ao instalar dependencias Python
    pause
    exit /b 1
)

echo [SUCCESS] Dependencias Python instaladas com sucesso!

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js nao encontrado. Instale Node.js primeiro.
    echo https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Node.js encontrado, instalando dependencias do frontend...
cd ..\frontend
npm install

if errorlevel 1 (
    echo [ERROR] Falha ao instalar dependencias Node.js
    pause
    exit /b 1
)

echo [SUCCESS] Dependencias Node.js instaladas com sucesso!

echo.
echo ====================================
echo  Instalacao Completa!
echo ====================================
echo.
echo Para executar o sistema:
echo 1. Backend:  cd backend ^&^& python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo 2. Frontend: cd frontend ^&^& npm start
echo.
pause