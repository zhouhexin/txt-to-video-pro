#!/bin/bash

echo "======================================"
echo "🎬 AI 视频生成平台 - 启动脚本"
echo "======================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python 依赖
echo "📦 检查后端依赖..."
if [ ! -d "backend/venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv backend/venv
fi

source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

# 检查 Node 依赖
echo "📦 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "安装 Node 依赖..."
    cd frontend
    npm install
    cd ..
fi

# 创建必要目录
mkdir -p backend/data
mkdir -p backend/output_tasks

# 启动后端
echo "🚀 启动后端服务..."
cd backend
python run.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 2

# 启动前端
echo "🚀 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================"
echo "✅ 服务启动成功!"
echo "======================================"
echo "📍 前端地址：http://localhost:5173"
echo "📍 后端 API: http://localhost:5000"
echo "======================================"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
wait
