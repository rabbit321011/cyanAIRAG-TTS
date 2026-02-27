@echo off
chcp 65001 > nul
echo ========================================
echo   启动 AIlibs 服务器
echo ========================================
echo.

echo [1/3] 激活虚拟环境...
call "E:\AIlibs\agent-env\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo 错误: 无法激活虚拟环境
    pause
    exit /b 1
)
echo ✓ 虚拟环境已激活
echo.

echo [2/3] 设置CUDA环境变量...
set CUDA_LAUNCH_BLOCKING=1
echo ✓ CUDA_LAUNCH_BLOCKING=1
echo.

echo [3/3] 启动服务器...
echo 服务器将在以下地址运行:
echo   - http://127.0.0.1:3723
echo   - http://192.168.1.47:3723
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

python run.py

pause