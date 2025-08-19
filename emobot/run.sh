#!/bin/bash

# Emobot 快速启动脚本

echo "🤖 正在启动 Emobot..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# 检查依赖
echo "🔍 检查依赖..."
pip install -q -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  警告：未找到 .env 文件"
    echo "请创建 .env 文件并配置必要的 API 密钥："
    echo ""
    echo "OPENAI_API_KEY=your-api-key-here"
    echo ""
    echo "是否继续？(y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "退出..."
        exit 1
    fi
fi

# 运行主程序
echo ""
echo "🚀 启动 Emobot..."
echo ""
python main.py "$@" 