#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将 Python 脚本打包成可执行文件
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """安装依赖"""
    print("安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def build_executable():
    """打包可执行文件"""
    print("开始打包...")
    
    # PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--console",  # 保留控制台窗口
        "--name", "resource_downloader",  # 可执行文件名
        "--add-data", "requirements.txt;.",  # 包含依赖文件
        "download_resources.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("打包完成！")
        
        # 查找生成的可执行文件
        dist_dir = Path("dist")
        if dist_dir.exists():
            exe_files = list(dist_dir.glob("resource_downloader*"))
            if exe_files:
                print(f"可执行文件位置: {exe_files[0].absolute()}")
                return True
        
        print("未找到生成的可执行文件")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

def main():
    print("=" * 50)
    print("资源下载器打包工具")
    print("=" * 50)
    
    # 检查文件
    if not Path("download_resources.py").exists():
        print("错误: 找不到 download_resources.py")
        return
    
    if not Path("requirements.txt").exists():
        print("错误: 找不到 requirements.txt")
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 打包
    if build_executable():
        print("\n" + "=" * 50)
        print("打包成功！")
        print("可执行文件在 dist/ 目录中")
        print("将可执行文件发给客户即可使用")
        print("=" * 50)
    else:
        print("打包失败！")

if __name__ == "__main__":
    main()