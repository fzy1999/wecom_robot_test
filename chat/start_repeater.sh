#!/bin/bash

# 企业微信复读机器人启动脚本

echo "======================================================"
echo "🤖 企业微信群机器人复读机启动脚本"
echo "======================================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 检查依赖包
echo "🔍 检查依赖包..."
if ! python3 -c "import flask, requests" &> /dev/null; then
    echo "⚠️  部分依赖包未安装，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败，请手动安装: pip3 install -r requirements.txt"
        exit 1
    fi
fi

echo "✅ 依赖包检查完成"

# 检查配置文件
if [ ! -f "wecom_config.json" ]; then
    echo "⚠️  未找到配置文件，启动配置向导..."
    python3 wecom_config.py
    if [ $? -ne 0 ]; then
        echo "❌ 配置失败"
        exit 1
    fi
fi

echo "✅ 配置文件检查完成"

# 启动机器人
echo "🚀 启动企业微信复读机器人..."
python3 run_wecom_bot.py

echo "👋 机器人已停止运行" 