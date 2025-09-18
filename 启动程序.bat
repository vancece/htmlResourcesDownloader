@echo off
chcp 65001 >nul
title 私有化部署资源下载器

echo ==================================================
echo 🚀 私有化部署资源下载器 - Windows版
echo ==================================================
echo.

REM 检查可执行文件是否存在
if exist "dist\resource_downloader.exe" (
    echo ✅ 找到程序文件，正在启动...
    echo.
    
    REM 运行程序
    "dist\resource_downloader.exe"
    
    echo.
    echo ==================================================
    echo ✅ 程序执行完毕！
    echo ==================================================
    echo.
    echo 📁 下载的资源保存在 downloaded_resources\ 目录中
    echo.
) else (
    echo ❌ 未找到程序文件 dist\resource_downloader.exe
    echo 请确保文件完整性
    echo.
)

echo 按任意键关闭窗口...
pause >nul