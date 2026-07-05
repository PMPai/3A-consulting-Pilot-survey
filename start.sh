#!/usr/bin/env bash
# AI 導入需求評估系統 — macOS 啟動腳本
set -e

cd "$(dirname "$0")"

echo "========================================"
echo "  AI 導入需求評估系統 — 啟動中"
echo "========================================"

# 檢查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "[錯誤] 找不到 Python 3，請先安裝 Python 3.9+。"
    echo "  建議使用 Homebrew 安裝：brew install python"
    read -p "按 Enter 鍵結束..."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "偵測到 Python $PY_VERSION"

# 建立虛擬環境（若不存在）
if [ ! -d "backend/.venv" ]; then
    echo "[1/3] 建立虛擬環境..."
    (cd backend && python3 -m venv .venv)
fi

# 安裝相依套件
if [ ! -f "backend/.venv/.installed" ]; then
    echo "[2/3] 安裝相依套件..."
    (
        cd backend
        source .venv/bin/activate
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        touch .installed
    )
    if [ $? -ne 0 ]; then
        echo "[錯誤] 套件安裝失敗。"
        read -p "按 Enter 鍵結束..."
        exit 1
    fi
else
    echo "[2/3] 相依套件已安裝，略過。"
fi

# 啟動伺服器
echo "[3/3] 啟動伺服器 (http://localhost:3535) ..."

# macOS 開啟瀏覽器
if command -v open &> /dev/null; then
    (sleep 3 && open "http://localhost:3535") &
fi

(
    cd backend
    source .venv/bin/activate
    exec python -m uvicorn main:app --host 0.0.0.0 --port 3535
)
