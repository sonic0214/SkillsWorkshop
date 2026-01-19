# 文章存储位置

## 当前配置

所有抓取的文章将保存到：

**`/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/`**

### 文件说明

- **articles.db** - SQLite数据库（主存储，包含所有文章详细信息）
- **articles.json** - JSON格式导出（易读，方便集成其他工具）

## 访问方式

### 1. 使用查看工具

```bash
cd /Users/admin/Project/ai-info-stream-collector-code

# 查看统计
python3 view_articles.py --stats

# 查看最新文章
python3 view_articles.py --latest 10
```

### 2. 直接访问文件

```bash
# 在Finder中打开
open "/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/"

# 查看JSON文件
cat "/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/articles.json" | jq .

# 查询数据库
sqlite3 "/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/articles.db" \
  "SELECT title, source FROM articles LIMIT 5;"
```

### 3. 在其他应用中使用

这个目录位于你的知识管理系统中，可以：
- 用Obsidian或其他笔记软件查看
- 用数据分析工具读取
- 集成到你的工作流中

## 修改存储位置

如需修改存储位置，编辑配置文件：

```yaml
# config.yaml 或 config_full.yaml
storage:
  output_file: "/path/to/your/articles.json"
  database: "/path/to/your/articles.db"
```

## 注意事项

- 目录会自动创建（如果不存在）
- 旧数据不会自动迁移，需要手动复制
- 确保目标目录有写入权限
