@echo off
REM Emobot 快速启动脚本 (Windows)

echo 🤖 正在启动 Emobot...
echo.

REM 检查虚拟环境
if not exist "venv\" (
    echo ⚠️  未找到虚拟环境，正在创建...
    python -m venv venv
    echo ✅ 虚拟环境创建完成
)

REM 激活虚拟环境
echo 📦 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo 🔍 检查依赖...
pip install -q -r requirements.txt

REM 检查环境变量
if not exist ".env" (
    echo.
    echo ⚠️  警告：未找到 .env 文件
    echo 请创建 .env 文件并配置必要的 API 密钥：
    echo.
    echo OPENAI_API_KEY=your-api-key-here
    echo.
    set /p response=是否继续？(y/n): 
    if /i not "%response%"=="y" (
        echo 退出...
        exit /b 1
    )
)

REM 运行主程序
echo.
echo 🚀 启动 Emobot...
echo.
python main.py %* 