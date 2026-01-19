 # Article Collection Skill
 
 自动抓取、翻译和存储来自40+个优质内容源的文章信息。
 
 ## 功能特点
 
 - 📰 **多源抓取**：支持RSS、API和网页抓取三种方式
 - 🌐 **自动翻译**：使用Google Translate自动将标题翻译为中文
 - 🔄 **增量更新**：智能去重，只保存新文章
 - ⏰ **定时执行**：每天自动运行，无需手动干预
 - 💾 **双重存储**：SQLite数据库 + JSON文件导出
 - 📊 **分类管理**：按类别组织文章（AI资讯、播客、思考写作等）
 
 ## 内容源
 
 ### AI技术与资讯类 (16个源)
 - TLDR AI, Ben's Bites, Hugging Face Papers
 - NLP Newsletter, Interconnects, One Useful Thing
 - Why Try AI, The Rundown AI, The Neuron Daily
 - AI Leadership Edge, ChinAI Newsletter, Memia
 - AI to ROI, Nate's Newsletter, AI Changes Everything
 - KDnuggets AI
 
 ### 播客类 (4个源)
 - Lex Fridman Podcast, Cognitive Revolution
 - 80,000 Hours Podcast, Latent Space Podcast
 
 ### 聚合平台 (6个源)
 - Hacker News, Product Hunt
 - HackerNoon (Life Hacking, Writing, Product Management)
 
 ### 思考与写作类 (8个源)
 - Wait But Why, James Clear 3-2-1
 - Farnam Street Brain Food, Austin Kleon
 - Paul Graham Essays, Scott H Young
 - Readwise Wise, Dan Koe Letters
 
 ### 其他专业内容 (2个源)
 - DC The Median, Mark McNeilly
 
 ## 安装
 
 ```bash
 # 克隆或进入项目目录
 cd ai-info-stream-collector-code
 
 # 安装依赖
 pip install -r requirements.txt
 ```
 
 ## 使用方法
 
 ### 单次运行（测试）
 
 ```bash
 python main.py --once
 ```
 
 ### 定时运行
 
 ```bash
 # 默认每天早上8点运行
 python main.py
 ```
 
 ### 测试模式
 
 编辑 `config.yaml`：
 
 ```yaml
 schedule:
   test_mode: true
   test_interval_minutes: 5  # 每5分钟运行一次
 ```
 
 然后运行：
 
 ```bash
 python main.py
 ```
 
 ## 配置说明
 
 编辑 `config.yaml` 自定义设置：
 
 ```yaml
 # 翻译设置
 translation:
   enabled: true  # 是否启用翻译
   target_language: "zh-CN"
 
 # 存储设置
 storage:
   output_file: "data/articles.json"
   database: "data/articles.db"
 
 # 调度设置
 schedule:
   daily_time: "08:00"  # 每天运行时间
 ```
 
 ## 输出格式
 
 ### SQLite数据库
 
 位置：`data/articles.db`
 
 表结构：
 - id (主键)
 - title (原标题)
 - title_cn (中文标题)
 - url (文章链接)
 - source (来源)
 - category (分类)
 - published_date (发布日期)
 - summary (摘要)
 - summary_cn (中文摘要)
 - author (作者)
 - scraped_at (抓取时间)
 
 ### JSON文件
 
 位置：`data/articles.json`
 
 格式：
 ```json
 {
   "total": 1234,
   "last_updated": "2026-01-19T12:00:00",
   "articles": [
     {
       "id": "abc123",
       "title": "Original Title",
       "title_cn": "原始标题",
       "url": "https://example.com/article",
       "source": "TLDR AI",
       "category": "AI技术与资讯",
       "published_date": "2026-01-19T10:00:00",
       "summary": "Article summary...",
       "summary_cn": "文章摘要...",
       "author": "John Doe",
       "scraped_at": "2026-01-19T12:00:00"
     }
   ]
 }
 ```
 
 ## 日志
 
 日志文件：`logs/collector.log`
 
 ## 项目结构
 
 ```
 ai-info-stream-collector-code/
 ├── config.yaml              # 配置文件
 ├── main.py                  # 主程序入口
 ├── requirements.txt         # Python依赖
 ├── README.md                # 文档
 ├── src/
 │   ├── collector.py         # 文章收集器
 │   ├── translator.py        # 翻译模块
 │   ├── storage.py           # 存储模块
 │   └── scrapers/
 │       ├── __init__.py
 │       ├── base.py          # 抓取器基类
 │       ├── rss_scraper.py   # RSS抓取器
 │       ├── web_scraper.py   # 网页抓取器
 │       └── api_scraper.py   # API抓取器
 ├── data/
 │   ├── articles.db          # SQLite数据库
 │   └── articles.json        # JSON导出
 └── logs/
     └── collector.log        # 运行日志
 ```
 
 ## 常见问题
 
 ### 1. 翻译速度慢
 
 免费翻译API有速率限制，代码中已加入延时。如需加速，可以：
 - 设置 `translation.enabled: false` 禁用翻译
 - 使用付费翻译API（需修改 `src/translator.py`）
 
 ### 2. 某些源抓取失败
 
 - 网页结构可能变化，需要更新选择器
 - 某些网站有反爬虫机制
 - 检查 `logs/collector.log` 查看详细错误
 
 ### 3. 如何添加新的内容源
 
 编辑 `config.yaml`，在 `sources` 列表中添加：
 
 ```yaml
 sources:
   - name: "新源名称"
     type: "rss"  # 或 web, api
     url: "https://example.com/feed"
     frequency: "daily"
     category: "分类名称"
 ```
 
 ## 后台运行
 
 ### 使用 systemd (Linux)
 
 创建 `/etc/systemd/system/article-collector.service`：
 
 ```ini
 [Unit]
 Description=Article Collection Skill
 After=network.target
 
 [Service]
 Type=simple
 User=your-user
 WorkingDirectory=/path/to/ai-info-stream-collector-code
 ExecStart=/usr/bin/python3 /path/to/ai-info-stream-collector-code/main.py
 Restart=always
 
 [Install]
 WantedBy=multi-user.target
 ```
 
 启动服务：
 ```bash
 sudo systemctl daemon-reload
 sudo systemctl enable article-collector
 sudo systemctl start article-collector
 ```
 
 ### 使用 launchd (macOS)
 
创建 `~/Library/LaunchAgents/com.ai-info-stream-collector-code.articlecollector.plist`：
 
 ```xml
 <?xml version="1.0" encoding="UTF-8"?>
 <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
 <plist version="1.0">
 <dict>
     <key>Label</key>
    <string>com.ai-info-stream-collector-code.articlecollector</string>
     <key>ProgramArguments</key>
     <array>
         <string>/usr/local/bin/python3</string>
         <string>/Users/admin/Project/ai-info-stream-collector-code/main.py</string>
     </array>
     <key>WorkingDirectory</key>
     <string>/Users/admin/Project/ai-info-stream-collector-code</string>
     <key>RunAtLoad</key>
     <true/>
     <key>KeepAlive</key>
     <true/>
 </dict>
 </plist>
 ```
 
 加载服务：
 ```bash
launchctl load ~/Library/LaunchAgents/com.ai-info-stream-collector-code.articlecollector.plist
 ```
 
 ## 许可证
 
 MIT
