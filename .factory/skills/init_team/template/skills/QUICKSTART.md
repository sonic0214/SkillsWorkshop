# VibeKit analyze_existing_project.py - 快速开始

5 分钟快速体验依赖分析工具！

## 步骤 1：安装依赖

```bash
# 安装 Python 包
pip install graphviz

# 安装系统依赖（可视化必需）
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz
```

## 步骤 2：创建测试项目

```bash
# 在 skills 目录下
cd /Users/admin/Project/MyBrain/skills/init_team/template/skills

# 创建一个包含循环依赖的测试项目
python3 create_test_project.py ./test_project
```

输出：
```
创建测试项目：./test_project
✅ 测试项目创建完成

项目结构：
  ./test_project/
    ├── auth/
    ├── user/
    ├── permission/
    ├── order/
    ├── payment/
    ├── utils/
    ├── api/
    ├── database/
    └── requirements.txt

运行分析：python analyze_existing_project.py ./test_project
```

## 步骤 3：运行分析

```bash
# 方法 1：直接运行（推荐）
python3 analyze_existing_project.py ./test_project

# 方法 2：使用测试脚本
./test_analyze.sh ./test_project
```

输出示例：
```
============================================================
  VibeKit - 项目依赖分析 v0.1
============================================================

🔍 扫描项目：/path/to/test_project
   技术栈：Python
   发现 8 个模块

🔗 分析依赖关系...
   发现 23 条依赖关系

🔄 检测循环依赖...
   ⚠️  发现 2 处循环依赖！

👑 检测上帝模块...
   ⚠️  发现 1 个上帝模块

📊 生成依赖图...
   ✅ 依赖图已保存：./test_project/.vibekit/dependency_graph.svg

📝 生成分析报告...
   ✅ 报告已保存：./test_project/.vibekit/analysis_report.md

============================================================
  ✅ 分析完成！
============================================================

查看报告：./test_project/.vibekit/analysis_report.md
查看依赖图：./test_project/.vibekit/dependency_graph.svg

⚠️  发现 2 处循环依赖（P0 问题）
```

## 步骤 4：查看报告

```bash
# 查看 Markdown 报告
cat ./test_project/.vibekit/analysis_report.md

# 或在编辑器中打开
code ./test_project/.vibekit/analysis_report.md

# 查看依赖图（SVG）
open ./test_project/.vibekit/dependency_graph.svg  # macOS
xdg-open ./test_project/.vibekit/dependency_graph.svg  # Linux
```

## 预期结果

### 循环依赖

测试项目包含 2 处循环依赖：

1. **auth ↔ user ↔ permission**
   ```
   auth/service.py → user/model.py → permission/check.py → auth/service.py
   ```

2. **order ↔ payment**
   ```
   order/model.py → payment/webhook.py → payment/processor.py → order/model.py
   ```

### 上帝模块

1. **utils** 模块
   - 被 6/8 个模块依赖（依赖率 75%）
   - 包含各种不相关的工具函数

## 步骤 5：分析您自己的项目

```bash
# 分析真实项目
python3 analyze_existing_project.py ~/your-project

# 查看报告
cat ~/your-project/.vibekit/analysis_report.md
```

## 常见问题

### Q: graphviz 安装失败？

**macOS**:
```bash
brew install graphviz
pip install graphviz
```

**Ubuntu**:
```bash
sudo apt-get install graphviz
pip install graphviz
```

**Windows**:
1. 下载：https://graphviz.org/download/
2. 安装并添加到 PATH
3. `pip install graphviz`

### Q: 为什么没发现我的模块？

检查：
1. 模块目录是否在 `src/`, `app/`, `lib/` 或根目录下
2. Python 包是否有 `__init__.py`
3. 模块名是否以 `.` 开头（会被忽略）

### Q: 分析报告在哪里？

所有输出都在项目的 `.vibekit/` 目录：
```
your-project/
├── .vibekit/
│   ├── analysis_report.md      # 主报告
│   ├── dependency_graph.svg    # 依赖图
│   └── dependency_data.json    # 原始数据
└── ...
```

## 下一步

- ✅ 查看报告，了解项目的架构问题
- ✅ 根据建议，开始重构
- ✅ 重新运行分析，验证改进

## 需要帮助？

- 查看详细文档：`ANALYZE_README.md`
- 报告问题：提供项目类型、规模、错误信息

---

*VibeKit v0.1 - 让 Vibe Coding 可持续*
