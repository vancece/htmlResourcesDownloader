#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 平台打包脚本
用于生成 resource_downloader.exe 可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        return False

def build_windows_exe():
    """构建 Windows 可执行文件"""
    print("开始构建 Windows 可执行文件...")
    
    # 确保在正确的目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 尝试找到 pyinstaller 的完整路径
    pyinstaller_cmd = None
    possible_paths = [
        "pyinstaller",
        "/Users/lianziyu/Library/Python/3.9/bin/pyinstaller",
        sys.executable.replace("python", "pyinstaller").replace("python3", "pyinstaller")
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                pyinstaller_cmd = path
                break
        except:
            continue
    
    if not pyinstaller_cmd:
        print("❌ 无法找到 pyinstaller 命令")
        return False
    
    # PyInstaller 命令参数 - 直接生成 .exe 文件
    cmd = [
        pyinstaller_cmd,
        "--onefile",                        # 打包成单个文件
        "--console",                        # 保留控制台窗口
        "--name", "resource_downloader.exe", # 输出文件名（带.exe后缀）
        "--distpath", "dist",               # 输出到 dist 目录
        "--clean",                          # 清理临时文件
        "--noconfirm",                      # 不询问覆盖
        "download_resources.py"             # 源文件
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Windows 可执行文件构建成功！")
            
            # 检查生成的文件
            exe_path = Path("dist/resource_downloader.exe")
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"📁 文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {file_size:.1f} MB")
                print(f"✅ Windows 可执行文件已生成: {exe_path.name}")
                return True
            else:
                print("❌ 未找到生成的可执行文件")
                return False
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ 未找到 pyinstaller 命令")
        return False
    except Exception as e:
        print(f"❌ 构建过程中出现错误: {e}")
        return False

def cleanup_build_files():
    """清理构建过程中的临时文件"""
    dirs_to_clean = ["build", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"🧹 已清理临时目录: {dir_name}")
    
    # 清理 spec 文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 已清理文件: {spec_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("🏗️  Windows 版本打包工具")
    print("=" * 60)
    print()
    
    # 检查并安装 PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装 PyInstaller，请手动安装后重试")
            return False
    
    # 检查源文件是否存在
    if not Path("download_resources.py").exists():
        print("❌ 未找到源文件 download_resources.py")
        return False
    
    # 构建可执行文件
    if not build_windows_exe():
        return False
    
    # 清理临时文件
    cleanup_build_files()
    
    print()
    print("=" * 60)
    print("🎉 Windows .exe 文件打包完成！")
    print("=" * 60)
    print()
    print("📁 输出文件: dist/resource_downloader.exe")
    print()
    print("🚀 现在可以将 resource_downloader.exe 发送给 Windows 用户了！")
    print("💡 Windows 用户使用方法：")
    print("   1. 将 resource_downloader.exe 复制到项目根目录")
    print("   2. 双击运行或在命令行中执行")
    print("   3. 等待下载完成")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        sys.exit(1)