#!/usr/bin/env bash
# Benchmark Hub 启动脚本
# 用法: bash start.sh [port]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

PORT="${1:-5000}"
CONDA_PY="/home/siqing/miniconda3/envs/protein-mcp/bin/python"

if [[ -x "$CONDA_PY" ]]; then
    PYTHON_BIN="$CONDA_PY"
else
    PYTHON_BIN="python3"
fi

# 检测依赖
"$PYTHON_BIN" -c "import flask, flask_cors, openpyxl" 2>/dev/null || {
    echo "正在安装依赖..."
    "$PYTHON_BIN" -m pip install -r requirements.txt
}

echo "启动 Benchmark Hub 平台 http://localhost:${PORT}"
exec "$PYTHON_BIN" app.py --port "$PORT"
