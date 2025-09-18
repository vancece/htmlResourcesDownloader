#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
私有化部署资源下载器
用于下载 HTML 文件中引用的所有外部 JavaScript 资源
"""

import os
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import List, Set, Tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

class ResourceDownloader:
    def __init__(self, base_dir: str = None):
        # 如果没有指定目录，尝试自动检测项目根目录
        if base_dir is None:
            current_dir = Path.cwd()
            # 如果当前目录有 index.html，就是项目根目录
            if (current_dir / "index.html").exists():
                self.base_dir = current_dir
            # 如果当前目录是 resource_downloader，则上级目录是项目根目录
            elif current_dir.name == "resource_downloader" and (current_dir.parent / "index.html").exists():
                self.base_dir = current_dir.parent
            else:
                # 让用户选择项目目录
                self.base_dir = self.find_project_directory()
        else:
            self.base_dir = Path(base_dir)
        
        self.download_dir = self.base_dir / "downloaded_resources"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('download_log.txt', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.total_urls = 0
        self.downloaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    def find_project_directory(self) -> Path:
        """查找项目根目录"""
        current = Path.cwd()
        
        # 向上查找包含 index.html 的目录
        for parent in [current] + list(current.parents):
            if (parent / "index.html").exists():
                print(f"找到项目根目录: {parent}")
                return parent
        
        # 如果没找到，让用户手动输入
        while True:
            user_input = input("请输入项目根目录路径（包含 index.html 的目录）: ").strip()
            if not user_input:
                continue
            
            project_dir = Path(user_input).expanduser().resolve()
            if project_dir.exists() and (project_dir / "index.html").exists():
                return project_dir
            else:
                print(f"错误: {project_dir} 不存在或不包含 index.html 文件")

    def find_html_files(self) -> List[Path]:
        """查找所有需要扫描的 HTML 文件"""
        html_files = []
        
        # 根目录的 index.html
        root_index = self.base_dir / "index.html"
        if root_index.exists():
            html_files.append(root_index)
            self.logger.info(f"找到根目录 HTML: {root_index}")
        
        # 一级子目录中的 index.html
        for item in self.base_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                sub_index = item / "index.html"
                if sub_index.exists():
                    html_files.append(sub_index)
                    self.logger.info(f"找到子目录 HTML: {sub_index}")
        
        self.logger.info(f"总共找到 {len(html_files)} 个 HTML 文件")
        return html_files

    def extract_script_urls(self, html_file: Path) -> Set[str]:
        """从 HTML 文件中提取所有外部 script 资源 URL"""
        urls = set()
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            script_tags = soup.find_all('script', src=True)
            
            for script in script_tags:
                src = script.get('src', '').strip()
                if not src:
                    continue
                
                # 判断是否为外部资源
                if self.is_external_url(src):
                    # 处理协议相对 URL
                    if src.startswith('//'):
                        src = 'https:' + src
                    
                    # 移除查询参数（如 ?v=1）
                    parsed = urlparse(src)
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    urls.add(clean_url)
                    self.logger.debug(f"提取到外部资源: {clean_url}")
                else:
                    self.logger.debug(f"跳过本地资源: {src}")
            
            self.logger.info(f"从 {html_file.name} 提取到 {len(urls)} 个外部资源")
            
        except Exception as e:
            self.logger.error(f"解析 {html_file} 时出错: {e}")
        
        return urls

    def is_external_url(self, url: str) -> bool:
        """判断是否为外部 URL"""
        if not url:
            return False
        
        # 外部 URL 的特征
        if url.startswith(('http://', 'https://', '//')):
            return True
        
        # 相对路径不是外部 URL
        if url.startswith(('/', './', '../')) or not url.startswith(('http', '//')):
            return False
        
        return True

    def get_local_path(self, url: str) -> Path:
        """根据 URL 生成本地文件路径"""
        parsed = urlparse(url)
        
        # 构建路径：domain/path
        domain = parsed.netloc
        path = parsed.path.lstrip('/')
        
        # 如果路径为空或以 / 结尾，添加默认文件名
        if not path or path.endswith('/'):
            path += 'index.js'
        
        local_path = self.download_dir / domain / path
        return local_path

    def download_file(self, url: str, local_path: Path, max_retries: int = 3) -> bool:
        """下载单个文件"""
        # 创建目录
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件已存在，跳过
        if local_path.exists():
            self.logger.info(f"文件已存在，跳过: {local_path.name}")
            self.skipped_count += 1
            return True
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"下载中 ({attempt + 1}/{max_retries}): {url}")
                
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                
                with open(local_path, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 显示进度
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\r  进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
                
                print()  # 换行
                self.logger.info(f"下载成功: {local_path.name}")
                self.downloaded_count += 1
                return True
                
            except Exception as e:
                self.logger.warning(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    self.logger.error(f"下载最终失败: {url}")
                    self.failed_count += 1
                    return False
        
        return False

    def run(self):
        """运行主程序"""
        self.logger.info("=" * 60)
        self.logger.info("私有化部署资源下载器启动")
        self.logger.info("=" * 60)
        
        # 1. 查找 HTML 文件
        html_files = self.find_html_files()
        if not html_files:
            self.logger.error("未找到任何 HTML 文件！")
            return
        
        # 2. 提取所有 URL
        all_urls = set()
        for html_file in html_files:
            urls = self.extract_script_urls(html_file)
            all_urls.update(urls)
        
        self.total_urls = len(all_urls)
        self.logger.info(f"总共找到 {self.total_urls} 个唯一的外部资源")
        
        if not all_urls:
            self.logger.info("没有找到需要下载的外部资源")
            return
        
        # 3. 创建下载目录
        self.download_dir.mkdir(exist_ok=True)
        self.logger.info(f"下载目录: {self.download_dir.absolute()}")
        
        # 4. 下载所有文件
        self.logger.info("开始下载资源...")
        for i, url in enumerate(sorted(all_urls), 1):
            self.logger.info(f"\n[{i}/{self.total_urls}] 处理: {url}")
            local_path = self.get_local_path(url)
            self.download_file(url, local_path)
        
        # 5. 输出统计信息
        self.logger.info("\n" + "=" * 60)
        self.logger.info("下载完成！统计信息：")
        self.logger.info(f"总资源数: {self.total_urls}")
        self.logger.info(f"下载成功: {self.downloaded_count}")
        self.logger.info(f"跳过已存在: {self.skipped_count}")
        self.logger.info(f"下载失败: {self.failed_count}")
        self.logger.info(f"下载目录: {self.download_dir.absolute()}")
        self.logger.info("=" * 60)
        
        # 6. 生成资源清单
        self.generate_manifest()

    def generate_manifest(self):
        """生成资源清单文件"""
        manifest_file = self.download_dir / "resource_manifest.txt"
        
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                f.write("私有化部署资源清单\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总资源数: {self.total_urls}\n")
                f.write(f"下载成功: {self.downloaded_count}\n")
                f.write(f"跳过已存在: {self.skipped_count}\n")
                f.write(f"下载失败: {self.failed_count}\n\n")
                
                f.write("资源目录结构:\n")
                f.write("-" * 30 + "\n")
                
                # 遍历下载目录，生成目录树
                for root, dirs, files in os.walk(self.download_dir):
                    level = root.replace(str(self.download_dir), '').count(os.sep)
                    indent = ' ' * 2 * level
                    f.write(f"{indent}{os.path.basename(root)}/\n")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files:
                        if file != "resource_manifest.txt":
                            f.write(f"{subindent}{file}\n")
            
            self.logger.info(f"资源清单已生成: {manifest_file}")
            
        except Exception as e:
            self.logger.error(f"生成资源清单失败: {e}")


def main():
    """主函数"""
    try:
        # 检查依赖
        try:
            import requests
            import bs4
        except ImportError as e:
            print(f"缺少依赖库: {e}")
            print("请安装依赖: pip install requests beautifulsoup4")
            sys.exit(1)
        
        # 运行下载器
        downloader = ResourceDownloader()
        downloader.run()
        
        print("\n按任意键退出...")
        input()
        
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
    except Exception as e:
        print(f"程序运行出错: {e}")
        print("\n按任意键退出...")
        input()


if __name__ == "__main__":
    main()