# 私有化部署资源下载器

## 功能说明

这个工具用于扫描项目中所有 HTML 文件的 `<script>` 标签，下载其中引用的所有外部 JavaScript 资源，以支持私有化部署。

## 工作原理

1. **扫描范围**：
   - 根目录的 `index.html`
   - 所有一级子目录中的 `index.html`

2. **资源识别**：
   - 提取所有 `<script src="...">` 中的外部 URL
   - 自动识别并排除相对路径资源（如 `/app-xxx/...`、`./file.js` 等）
   - 支持协议相对 URL（如 `//domain.com/file.js`）

3. **下载策略**：
   - 保持原有的域名和路径结构
   - 自动创建对应的文件夹层级
   - 支持断点续传和失败重试

## 使用方法

### 方法一：直接运行可执行文件（推荐）

1. 将 `resource_downloader.exe`（Windows）或 `resource_downloader`（Mac/Linux）放到项目根目录
2. 双击运行或在命令行中执行：
   ```bash
   # Windows
   resource_downloader.exe
   
   # Mac/Linux
   ./resource_downloader
   ```

### 方法二：运行 Python 脚本

1. 确保已安装 Python 3.6+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行脚本：
   ```bash
   python download_resources.py
   ```

## 输出结果

运行完成后，会在当前目录生成：

```
downloaded_resources/
├── static.cloudbase.net/
│   └── cloudbase-js-sdk/
│       └── 2.20.12/
│           └── cloudbase.full.js
├── qbase.cdn-go.cn/
│   └── lcap/
│       └── lcap-resource-cdngo/
│           ├── -/release/_npm/react@16.14.0/umd/
│           │   └── react.production.min.js
│           └── -/0.1.2/_url/ajax/libs/mobx/5.15.7/
│               └── mobx.umd.js
├── tam.cdn-go.cn/
│   └── aegis-sdk/
│       └── latest/
│           └── aegis.min.js
├── resource_manifest.txt  # 资源清单
└── download_log.txt       # 下载日志
```

## 日志文件

- `download_log.txt`：详细的下载日志，包含成功、失败、跳过的文件信息
- `resource_manifest.txt`：资源清单，包含目录结构和统计信息

## 注意事项

1. **网络环境**：确保运行环境可以访问外部网络
2. **磁盘空间**：确保有足够的磁盘空间存储下载的资源
3. **重复运行**：已下载的文件会自动跳过，可以安全地重复运行
4. **失败重试**：网络异常时会自动重试，最多重试 3 次

## 常见问题

### Q: 下载失败怎么办？
A: 检查网络连接，查看 `download_log.txt` 了解具体错误信息。可以重新运行程序，已下载的文件会自动跳过。

### Q: 如何在私有化服务器上使用这些资源？
A: 将 `downloaded_resources` 文件夹部署到你的私有化服务器上，然后配置 Web 服务器（如 Nginx）提供静态文件服务。

### Q: 程序运行很慢？
A: 这是正常现象，因为需要下载大量文件。程序会显示实时进度，请耐心等待。

## 技术支持

如有问题，请查看：
1. `download_log.txt` - 详细的运行日志
2. `resource_manifest.txt` - 资源清单和统计信息

## 版本信息

- 版本：1.0.0
- 支持平台：Windows、macOS、Linux
- Python 版本要求：3.6+