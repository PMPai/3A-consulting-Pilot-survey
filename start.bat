@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   AI 導入需求評估系統 — 啟動中
echo ========================================

REM 檢查 Python
where python >nul 2>nul
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.9+ 並加入 PATH。
    pause
    exit /b 1
)

REM 建立虛擬環境（若不存在）
if not exist "backend\.venv" (
    echo [1/3] 建立虛擬環境...
    pushd backend
    python -m venv .venv
    popd
)

REM 安裝相依套件
if not exist "backend\.venv\.installed" (
    echo [2/3] 安裝相依套件...
    pushd backend
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip >nul
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [錯誤] 套件安裝失敗。
        pause
        exit /b 1
    )
    echo installed > .installed
    popd
) else (
    echo [2/3] 相依套件已安裝，略過。
)

REM 啟動伺服器
echo [3/3] 啟動伺服器 (http://localhost:3535) ...
start "" http://localhost:3535
pushd backend
call .venv\Scripts\activate.bat
python -m uvicorn main:app --host 0.0.0.0 --port 3535
popd
pause
