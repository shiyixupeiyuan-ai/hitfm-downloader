@echo off
chcp 65001 >nul
cd /d "%～dp0"

:: ============= 用户输入 =============
echo.
echo 📻 HITFM 节目下载器配置
echo.

set /p START_DATE=起始日期 (格式 YYYY-MM-DD，默认 2025-11-01): 
if "%START_DATE%"=="" set START_DATE=2025-11-01

set /p END_DATE=结束日期 (格式 YYYY-MM-DD，默认 2025-11-30): 
if "%END_DATE%"=="" set END_DATE=2025-11-30

set /p SAVE_DIR=保存目录 (默认 HITFM_202512): 
if "%SAVE_DIR%"=="" set SAVE_DIR=HITFM_202512

:: 自动转为 ./HITFM_xxx 格式
set SAVE_BASE_DIR=./%SAVE_DIR%

:: ============= 生成 config.py =============
(
echo START_DATE = "%START_DATE%"
echo END_DATE = "%END_DATE%"
echo CHANNEL_NAME = "662"
echo SAVE_BASE_DIR = "%SAVE_BASE_DIR%"
) > config.py

:: ============= 运行程序============
:RUN
python hitfm_downloader.py
if %errorlevel% EQU 0 goto :EOF

:: 检查是否是模块缺失错误
python -c "import sys; print('MODULE_MISSING' if 'ModuleNotFoundError' in str(sys.exc_info()[1]) else 'OTHER_ERROR')" 2>nul | findstr /C:"MODULE_MISSING" >nul
if %errorlevel% EQU 0 (
    echo.
    echo ⚠️  检测到缺少Python依赖，正在自动安装...
    pip install -r requirements.txt
    if %errorlevel% NEQ 0 (
        echo ❌ 依赖安装失败，请手动运行：pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功，重新运行脚本...
    goto RUN
) else (
    echo ❌ 脚本运行出错，请查看上方错误信息。
    pause
    exit /b 1
)

echo.
echo ✅ 依赖已就绪，开始下载节目...
echo.

:: 运行主脚本
python hitfm_downloader.py

:: ============= 清理（可选）============
:: del config.py

echo.
echo 🎉 脚本执行完毕！
echo 按任意键退出...
pause >nul