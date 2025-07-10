#!/bin/bash

# 易事厅第三方机器人API启动脚本

echo "🚀 启动易事厅第三方机器人API..."
echo "=================================="

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip未安装，请先安装pip"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖包..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 启动服务
echo "🌟 启动Flask服务..."
echo "服务地址: http://localhost:8080"
echo "健康检查: http://localhost:8080/health"
echo "=================================="
echo ""

python3 server.py 