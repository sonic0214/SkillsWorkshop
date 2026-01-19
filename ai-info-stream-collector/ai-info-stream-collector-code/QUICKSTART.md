# 快速开始

## 5分钟上手指南

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试（无翻译，6个源）

```bash
python3 main.py --once
```

这将抓取约50篇文章，耗时约10秒。

### 3. 查看结果

```bash
# 查看统计信息
python3 view_articles.py --stats

# 查看最新10篇文章
python3 view_articles.py --latest 10
```

### 4. 启用翻译

编辑 `config.yaml`:

```yaml
translation:
  enabled: true  # 改为 true
```

再次运行:

```bash
python3 main.py --once
```

**注意**: 翻译需要较长时间，且可能受Google Translate速率限制影响。

### 5. 定时运行

```bash
# 每天早上8点自动运行
python3 main.py
```

按 Ctrl+C 停止。

### 6. 测试模式（每5分钟运行一次）

编辑 `config.yaml`:

```yaml
schedule:
  test_mode: true
  test_interval_minutes: 5
```

然后运行:

```bash
python3 main.py
```

## 配置文件说明

- `config.yaml` - 默认配置（6个主要源，快速测试）
- `config_full.yaml` - 完整配置（20+个源，包含所有类别）

使用完整配置:

```bash
python3 main.py --config config_full.yaml --once
```

## 输出文件

- `data/articles.db` - SQLite数据库（主存储）
- `data/articles.json` - JSON导出（方便阅读和集成）
- `logs/collector.log` - 运行日志

## 常见问题

### Q: 翻译太慢？
A: 设置 `translation.enabled: false` 禁用翻译

### Q: 某些源抓取失败？
A: 检查 `logs/collector.log` 查看详细错误信息

### Q: 如何添加新源？
A: 在 `config.yaml` 的 `sources` 列表中添加:

```yaml
sources:
  - name: "新源名称"
    type: "rss"  # 或 web, api
    url: "https://example.com/feed"
    category: "分类名称"
```

### Q: 如何后台运行？
A: 参考 README.md 中的系统服务配置（systemd/launchd）

## 项目结构

```
ai-info-stream-collector-code/
├── config.yaml           # 默认配置
├── config_full.yaml      # 完整配置
├── main.py               # 主程序
├── view_articles.py      # 查看工具
├── requirements.txt      # 依赖列表
├── src/
│   ├── collector.py      # 收集器
│   ├── translator.py     # 翻译器
│   ├── storage.py        # 存储
│   └── scrapers/         # 抓取器
├── data/                 # 数据文件
└── logs/                 # 日志文件
```
