#!/bin/bash
# 私有化部署资源下载器 - macOS 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到脚本目录
cd "$SCRIPT_DIR"

echo "=================================================="
echo "🚀 私有化部署资源下载器"
echo "=================================================="
echo ""

# 检查可执行文件是否存在
if [ -f "dist/resource_downloader" ]; then
    echo "✅ 找到程序文件，正在启动..."
    echo ""
    
    # 给可执行文件添加执行权限
    chmod +x dist/resource_downloader
    
    # 运行程序
    ./dist/resource_downloader
    
    echo ""
    echo "=================================================="
    echo "✅ 程序执行完毕！"
    echo "=================================================="
    echo ""
    echo "📁 下载的资源保存在 downloaded_resources/ 目录中"
    echo ""
else
    echo "❌ 未找到程序文件 dist/resource_downloader"
    echo "请确保文件完整性"
    echo ""
fi

echo "按任意键关闭窗口..."
read -n 1 -s