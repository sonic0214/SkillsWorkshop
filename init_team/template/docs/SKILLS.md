# Project Team System - Skills Reference

v3.0 - Complete Skill Scripts Documentation

> 本文档提供 8 个 Skill 脚本的完整参考

## 目录

- [1. build_main_index.py](#1-build_main_indexpy) - 构建主索引
- [2. build_module_index.py](#2-build_module_indexpy) - 构建模块索引
- [3. search_in_module.py](#3-search_in_modulepy) - 模块内搜索
- [4. compress_context.py](#4-compress_contextpy) - 压缩上下文
- [5. run_tdd_cycle.py](#5-run_tdd_cyclepy) - 执行 TDD 流程
- [6. checkpoint.py](#6-checkpointpy) - 快照管理
- [7. init_new_project.py](#7-init_new_projectpy) - 初始化新项目
- [8. init_existing_project.py](#8-init_existing_projectpy) - 分析存量项目
- [9. analyze_existing_project.py](#9-analyze_existing_projectpy) - 架构深度分析
- [10. generate_test_template.py](#10-generate_test_templatepy) - 生成测试模板

---

## 1. build_main_index.py

### 功能
构建项目主索引 (模块级),供 Architect Mode 使用。

### 使用场景
- 项目初始化时
- 新增模块后
- Architect Mode 需要查看项目全貌

### 命令行
```bash
python skills/build_main_index.py <project_root>
```

### 输入
- `<project_root>`: 项目根目录
- 自动扫描 `src/` 目录下的所有模块

### 输出
- `.context/main_index.json`: 主索引文件

### 输出格式
```json
{
  "project_name": "my-project",
  "created_at": "2024-12-04T10:00:00",
  "modules": {
    "auth": {
      "path": "src/auth",
      "purpose": "用户认证模块",
      "layers": ["api", "models", "services"],
      "module_index": ".context/modules/auth_index.json"
    },
    "payment": {
      "path": "src/payment",
      "purpose": "支付处理模块",
      "layers": ["api", "models", "services"],
      "module_index": ".context/modules/payment_index.json"
    }
  },
  "module_count": 2
}
```

### 算法
1. 扫描 `src/` 目录,识别所有模块 (子目录)
2. 对每个模块:
   - 提取模块名
   - 识别分层结构 (api/, models/, services/ 等)
   - 生成模块索引指针
3. 生成 JSON 并保存

### 复杂度
- 时间: O(m),m = 模块数量
- 空间: O(m)

### 示例
```bash
# 项目结构
src/
├── auth/
│   ├── api/
│   ├── models/
│   └── services/
└── payment/
    ├── api/
    └── models/

# 执行
python skills/build_main_index.py .

# 输出
✓ 扫描到 2 个模块: auth, payment
✓ 主索引已生成: .context/main_index.json
```

### 设计原则
- **模块级粒度**: 只扫描模块,不深入文件
- **指针引用**: 指向模块索引,不包含完整内容
- **快速扫描**: O(m) 复杂度,适合频繁调用

---

## 2. build_module_index.py

### 功能
构建模块索引 (文件级),供 Dev Mode 使用。

### 使用场景
- Dev Mode 开始开发某个模块前
- 模块文件结构变化后
- 需要搜索模块内符号时

### 命令行
```bash
python skills/build_module_index.py <project_root> <module_name>
```

### 输入
- `<project_root>`: 项目根目录
- `<module_name>`: 模块名 (如 "auth")

### 输出
- `.context/modules/{module}_index.json`: 模块索引文件

### 输出格式
```json
{
  "module_name": "auth",
  "created_at": "2024-12-04T10:05:00",
  "layers": {
    "api": {
      "files": [
        {
          "path": "src/auth/api/login.py",
          "exports": ["login_handler", "logout_handler"],
          "lines": 120,
          "last_modified": "2024-12-04T09:30:00"
        }
      ]
    },
    "models": {
      "files": [
        {
          "path": "src/auth/models/user.py",
          "exports": ["User", "UserRole"],
          "lines": 80,
          "last_modified": "2024-12-04T09:00:00"
        }
      ]
    }
  },
  "file_count": 8
}
```

### 算法
1. 扫描 `src/{module}/` 目录,识别所有分层
2. 对每个 Python 文件:
   - 使用 AST 解析
   - 提取导出的函数和类 (非私有,不以 _ 开头)
   - 统计行数
   - 获取修改时间
3. 按分层组织,生成 JSON

### 复杂度
- 时间: O(f),f = 模块内文件数
- 空间: O(f + s),s = 符号数量

### AST 解析示例
```python
import ast

def extract_exports(file_path: Path) -> list:
    """提取文件导出的符号 (函数/类)"""
    tree = ast.parse(file_path.read_text())
    exports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):
                exports.append(node.name)
        elif isinstance(node, ast.ClassDef):
            exports.append(node.name)
    return exports
```

### 示例
```bash
# 执行
python skills/build_module_index.py . auth

# 输出
✓ 扫描模块: auth
✓ 发现 3 个分层: api, models, services
✓ 解析 8 个文件
✓ 提取 24 个导出符号
✓ 模块索引已生成: .context/modules/auth_index.json
```

### 设计原则
- **文件级粒度**: 列出所有文件及其导出符号
- **AST 解析**: 准确提取符号,不依赖正则
- **按层组织**: 保持分层结构清晰

---

## 3. search_in_module.py

### 功能
在模块内搜索文件、符号或读取文件内容。

### 使用场景
- Dev Mode 需要定位某个函数/类
- 需要查看某个分层的所有文件
- 按需读取文件完整内容

### 命令行
```bash
# 列出分层的所有文件
python skills/search_in_module.py <project_root> <module> list_files:<layer>

# 查找符号定义
python skills/search_in_module.py <project_root> <module> find_symbol:<name>

# 读取文件
python skills/search_in_module.py <project_root> <module> read_file:<path>
```

### 查询类型

#### 1. list_files:<layer>
列出某个分层的所有文件

**示例**:
```bash
python skills/search_in_module.py . auth list_files:api
```

**输出**:
```json
{
  "query": "list_files:api",
  "results": [
    {
      "path": "src/auth/api/login.py",
      "exports": ["login_handler", "logout_handler"],
      "lines": 120
    },
    {
      "path": "src/auth/api/register.py",
      "exports": ["register_handler"],
      "lines": 80
    }
  ]
}
```

#### 2. find_symbol:<name>
查找符号 (函数/类) 定义的位置

**示例**:
```bash
python skills/search_in_module.py . auth find_symbol:login_handler
```

**输出**:
```json
{
  "query": "find_symbol:login_handler",
  "results": [
    {
      "path": "src/auth/api/login.py",
      "symbol": "login_handler",
      "line": 45
    }
  ]
}
```

#### 3. read_file:<path>
读取文件完整内容

**示例**:
```bash
python skills/search_in_module.py . auth read_file:api/login.py
```

**输出**:
```json
{
  "query": "read_file:api/login.py",
  "path": "src/auth/api/login.py",
  "content": "async def login_handler(request):\n    ...",
  "lines": 120
}
```

### 算法
1. 加载模块索引 `.context/modules/{module}_index.json`
2. 根据查询类型:
   - `list_files`: 过滤指定分层
   - `find_symbol`: 遍历所有文件的 exports
   - `read_file`: 读取文件系统
3. 返回 JSON 结果

### 复杂度
- `list_files`: O(f),f = 分层内文件数
- `find_symbol`: O(s),s = 符号总数
- `read_file`: O(1) + 文件大小

### 设计原则
- **按需检索**: 只返回请求的信息
- **JSON 输出**: 便于程序解析
- **多种查询**: 支持不同粒度的搜索

---

## 4. compress_context.py

### 功能
压缩任务上下文,使用指针式引用替代完整内容。

### 使用场景
- 创建新任务时
- 上下文过大需要压缩
- 传递任务给 Dev Mode

### 命令行
```bash
python skills/compress_context.py <project_root> <task_id>
```

### 输入
- `<project_root>`: 项目根目录
- `<task_id>`: 任务 ID (如 "task_001")

### 输出
- `.context/tasks/{task_id}_compressed.json`: 压缩后的上下文

### 压缩策略

#### 传统方式 (未压缩)
```json
{
  "task_id": "task_001",
  "files": {
    "login.py": "<完整的 500 行代码>",
    "user.py": "<完整的 300 行代码>"
  }
}
```

#### 指针式 (压缩后)
```json
{
  "task_id": "task_001",
  "context_pointers": [
    {
      "pointer": "src/auth/api/login.py#login_handler",
      "preview": "async def login_handler(request):\n    # 处理登录请求\n    ...",
      "full_path": "src/auth/api/login.py",
      "lines": "45-120",
      "on_demand": true
    },
    {
      "pointer": "src/auth/models/user.py#User",
      "preview": "class User:\n    # 用户模型\n    ...",
      "full_path": "src/auth/models/user.py",
      "lines": "10-80",
      "on_demand": true
    }
  ],
  "compressed_size": "2 KB",
  "original_size": "800 KB",
  "compression_ratio": 400
}
```

### 算法
1. 读取任务上下文 `.context/tasks/{task_id}.json`
2. 对每个文件:
   - 提取关键符号 (函数/类定义)
   - 生成预览 (前 500 字符)
   - 创建指针 `file_path#symbol`
3. 保存压缩后的上下文

### 复杂度
- 时间: O(n),n = 上下文中文件数
- 空间: O(1),指针大小固定

### 示例
```bash
# 执行
python skills/compress_context.py . task_001

# 输出
✓ 读取任务上下文: task_001
✓ 原始大小: 800 KB (2 个文件,800 行代码)
✓ 压缩后: 2 KB (2 个指针,50 行预览)
✓ 压缩比: 400:1
✓ 已保存: .context/tasks/task_001_compressed.json
```

### 设计原则
- **insight_012**: 传递指针,而非完整内容
- **预览机制**: 99% 情况下预览足够
- **按需检索**: 需要时使用 `search_in_module.py read_file`

---

## 5. run_tdd_cycle.py

### 功能
执行严格的 TDD 工作流: Red → Green → Refactor。

### 使用场景
- Dev Mode 开发新功能
- 确保 TDD 流程不被跳过
- 自动化测试和实现

### 命令行
```bash
python skills/run_tdd_cycle.py <project_root> <task_id>
```

### 输入
- `<project_root>`: 项目根目录
- `<task_id>`: 任务 ID (如 "task_001")

### 输出
- 测试结果
- TDD 日志
- 更新 `.context/tasks/{task_id}.json`

### TDD 三阶段

#### Phase 1: Red (必须失败)
```
┌─────────────────────────────────────────┐
│ Red Phase                               │
├─────────────────────────────────────────┤
│ 1. 引导编写测试文件                      │
│ 2. 运行 pytest                          │
│ 3. 验证测试失败 (FAIL)                  │
│ 4. 如果通过 → 提示测试无效              │
└─────────────────────────────────────────┘
```

**检查**:
```bash
pytest tests/auth/api/test_login.py
# 必须输出: FAILED
```

**如果 PASS**: 提示 "测试无效,请确保测试能检测到未实现的功能"

#### Phase 2: Green (通过测试)
```
┌─────────────────────────────────────────┐
│ Green Phase                             │
├─────────────────────────────────────────┤
│ 1. 引导编写最小实现                      │
│ 2. 运行 pytest                          │
│ 3. 验证测试通过 (PASS)                  │
│ 4. 如果失败 → 继续实现                  │
└─────────────────────────────────────────┘
```

**检查**:
```bash
pytest tests/auth/api/test_login.py
# 必须输出: PASSED
```

#### Phase 3: Refactor (可选)
```
┌─────────────────────────────────────────┐
│ Refactor Phase                          │
├─────────────────────────────────────────┤
│ 1. 询问是否需要重构                      │
│ 2. 如果需要,引导重构                     │
│ 3. 运行 pytest                          │
│ 4. 确保仍然通过 (PASS)                  │
└─────────────────────────────────────────┘
```

### 工作流程
```python
def run_tdd_cycle(project_root, task_id):
    # Phase 1: Red
    print("=== Red Phase ===")
    print("请编写测试文件...")
    input("按 Enter 继续运行测试")

    result = run_pytest()
    if result == "PASS":
        print("❌ 测试无效! 测试应该失败")
        return
    print("✓ 测试失败 (符合预期)")

    # Phase 2: Green
    print("\n=== Green Phase ===")
    print("请实现功能...")
    input("按 Enter 继续运行测试")

    result = run_pytest()
    if result == "FAIL":
        print("❌ 测试仍然失败,请继续实现")
        return
    print("✓ 测试通过")

    # Phase 3: Refactor
    print("\n=== Refactor Phase ===")
    refactor = input("是否需要重构? (y/n): ")
    if refactor == 'y':
        print("请进行重构...")
        input("按 Enter 继续运行测试")
        result = run_pytest()
        if result == "PASS":
            print("✓ 重构后测试仍然通过")
```

### 示例
```bash
# 执行
python skills/run_tdd_cycle.py . task_001

# 输出
=== Red Phase ===
请编写测试: tests/auth/api/test_login.py
[按 Enter 继续]
运行测试...
❌ FAILED (符合预期)
✓ Red Phase 完成

=== Green Phase ===
请实现功能: src/auth/api/login.py
[按 Enter 继续]
运行测试...
✓ PASSED
✓ Green Phase 完成

=== Refactor Phase ===
是否需要重构? (y/n): n
✓ TDD 循环完成
```

### 设计原则
- **严格流程**: 必须按 Red → Green → Refactor
- **自动验证**: 脚本验证每个阶段的结果
- **交互式**: 在每个阶段等待用户操作

---

## 6. checkpoint.py

### 功能
管理项目状态快照,支持保存和恢复。

### 使用场景
- 完成某个 phase 后保存状态
- 需要回滚到之前的状态
- 查看历史快照

### 命令行
```bash
# 保存快照
python skills/checkpoint.py save <project_root> <checkpoint_name>

# 列出所有快照
python skills/checkpoint.py list <project_root>

# 恢复快照
python skills/checkpoint.py restore <project_root> <checkpoint_name>
```

### 快照内容
```json
{
  "checkpoint_name": "plan_complete",
  "created_at": "2024-12-04T12:00:00",
  "phase": "plan",
  "project_state": {
    "current_phase": "plan",
    "modules": ["auth", "payment"],
    "tasks_completed": 0,
    "tasks_total": 5
  },
  "context_pointers": [
    {
      "type": "main_index",
      "path": ".context/main_index.json"
    },
    {
      "type": "requirements",
      "path": "requirements.md"
    }
  ],
  "git_commit": "abc123def456"
}
```

### 算法

#### 保存快照
1. 读取当前项目状态 `.project_state.json`
2. 创建上下文指针列表 (不保存完整内容)
3. 可选: 创建 git commit
4. 保存到 `.checkpoints/{name}_{timestamp}.json`

#### 列出快照
1. 扫描 `.checkpoints/` 目录
2. 读取所有 JSON 文件
3. 按时间排序显示

#### 恢复快照
1. 读取快照文件
2. 恢复 `.project_state.json`
3. 可选: git checkout 到对应 commit

### 示例

#### 保存快照
```bash
python skills/checkpoint.py save . plan_complete

# 输出
✓ 读取项目状态
✓ 创建上下文指针 (5 个文件)
✓ Git commit: abc123def456
✓ 快照已保存: .checkpoints/plan_complete_20241204_120000.json
```

#### 列出快照
```bash
python skills/checkpoint.py list .

# 输出
=== 项目快照列表 ===

1. plan_complete (2024-12-04 12:00:00)
   - Phase: plan
   - Tasks: 0/5
   - Git: abc123def456

2. implement_auth (2024-12-04 14:30:00)
   - Phase: implement
   - Tasks: 1/5
   - Git: def456ghi789

3. test_passed (2024-12-04 16:00:00)
   - Phase: test
   - Tasks: 5/5
   - Git: ghi789jkl012
```

### 设计原则
- **指针式快照**: 不保存完整内容,只保存指针
- **Git 集成**: 可选绑定 git commit
- **轻量级**: 每个快照 < 10 KB

---

## 7. create_project_structure.py

### 功能
从模板创建新项目结构。

### 使用场景
- 创建新项目
- 初始化项目目录和文件
- 复制模板并自定义

### 命令行
```bash
python skills/create_project_structure.py <project_name> [target_dir]
```

### 输入
- `<project_name>`: 项目名称 (如 "my-todo-app")
- `[target_dir]`: 目标目录 (默认当前目录)

### 输出
- 完整的项目目录结构
- 初始化的 Git 仓库
- 自定义的配置文件

### 模板结构
```
template/
├── .context/
│   └── modules/.gitkeep
├── .checkpoints/.gitkeep
├── skills/.gitkeep
├── .project_state.json
├── sop.yaml
├── requirements.md
└── README.md
```

### 创建流程
1. 从 `project_template/` 目录复制完整结构
2. 创建额外目录 `src/`, `tests/`
3. 更新 `.project_state.json`:
   - 设置 project_name
   - 设置 created_at
4. 更新 `README.md`:
   - 替换 "template" 为实际项目名
5. 初始化 Git 仓库

### 算法
```python
def create_project_structure(project_name, target_dir):
    template_dir = Path(__file__).parent.parent / "template"
    project_dir = Path(target_dir) / project_name

    # 1. 复制模板
    shutil.copytree(
        template_dir,
        project_dir,
        ignore=shutil.ignore_patterns('__pycache__', '*.pyc')
    )

    # 2. 创建额外目录
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()

    # 3. 更新配置
    update_project_state(project_dir, project_name)
    update_readme(project_dir, project_name)

    # 4. Git 初始化
    init_git_repo(project_dir)
```

### 示例
```bash
# 执行
python skills/create_project_structure.py my-todo-app

# 输出
📦 从模板创建项目: my-todo-app
📁 模板: /path/to/template
📁 目标: /path/to/my-todo-app

  ✓ 项目结构创建完成

🌳 初始化 Git 仓库...
  ✓ Git 仓库初始化完成

============================================================
✅ 项目 my-todo-app 创建完成！
============================================================

📁 位置: /path/to/my-todo-app

📂 目录结构:
  ├── .project_state.json  # 项目状态
  ├── .context/            # 上下文索引
  ├── .checkpoints/        # 状态快照
  ├── src/                 # 源代码
  ├── tests/               # 测试代码
  ├── sop.yaml             # 开发流程
  ├── requirements.md      # 需求文档
  └── README.md

🚀 下一步:
  cd my-todo-app
  vim requirements.md      # 1. 编写需求
  # 2. 按 SOP 流程开发
```

### 设计原则
- **模板驱动**: 从 `project_template/` 复制,避免硬编码
- **自定义**: 替换项目名等变量
- **Git 自动初始化**: 首次 commit 包含完整模板

---

## 7. init_new_project.py

### 功能
初始化新项目结构，基于标准模板创建完整的项目骨架。

### 使用场景
- Agent 检测到空项目目录
- 用户确认需要初始化新项目
- 创建与 project_team 同级的新项目

### 触发条件
Agent 自动检测并询问：
- 检测到目录为空或只有基础配置文件
- 询问："检测到空项目，是否使用 VibeKit 初始化新项目？"
- 用户确认后执行

### 命令行
```bash
python project_team/skills/init_new_project.py <project_name> [target_dir]
```

### 输入
- `<project_name>`: 新项目名称
- `[target_dir]`: 目标目录（默认为当前目录）

### 输出
- 完整的项目结构（src/, tests/, docs/ 等）
- 按 5 Phase 组织的文档模板
- Git 仓库初始化

### 项目结构
```
project_name/
├── .project_state.json     # 项目状态
├── .context/              # 项目上下文索引
├── .checkpoints/          # 项目状态快照
├── src/                   # 源代码
├── tests/                 # 测试代码
├── docs/                  # 项目文档（按 5 Phase 组织）
│   ├── 01_specify/        # 需求阶段
│   ├── 02_plan/          # 设计阶段
│   ├── 03_implement/     # 开发阶段
│   ├── 04_test/          # 测试阶段
│   ├── 05_release/       # 发布阶段
│   └── artifacts/        # 产出物
├── sop.yaml              # 开发流程
├── requirements.md       # 需求文档
└── README.md
```

### 设计原则
- **标准模板**: 基于最佳实践的项目结构
- **5 Phase 文档**: 遵循开发流程组织文档
- **与 project_team 同级**: 便于管理和使用

---

## 8. init_existing_project.py

### 功能
分析存量项目结构，生成项目初始化架构梳理文档。

### 使用场景
- Agent 检测到存量项目（有现有代码）
- 用户希望了解项目架构现状
- 重构前的架构评估

### 触发条件
Agent 询问后执行：
- 检测到目录有现有代码文件
- 询问："检测到存量项目，是否进行架构分析？"
- 用户确认后执行

### 命令行
```bash
python project_team/skills/init_existing_project.py /path/to/existing/project
```

### 输入
- 项目路径（绝对或相对路径）

### 输出
- `PROJECT_ARCHITECTURE_ANALYSIS.md`: 架构梳理报告
- `.vibekit/vibekit.yaml`: VibeKit 配置文件
- `.vibekit/analysis_data.json`: 分析数据（如果可用）

### 分析内容
1. **技术栈检测**
   - 编程语言和文件分布
   - 框架和库识别
   - 构建工具和包管理器
   - 测试框架检测

2. **项目结构分析**
   - 目录结构和用途分析
   - 关键配置文件识别
   - 架构模式检测

3. **架构质量评估**
   - 循环依赖检测（如果启用 VibeKit）
   - 上帝模块识别
   - 代码复杂度分析

4. **开发环境建议**
   - 推荐工具链
   - VibeKit 集成方案
   - 结构优化建议

### 输出示例
```markdown
# 项目架构梳理报告

## 📋 项目概览
**项目名称**: my-awesome-project
**项目路径**: /path/to/my-awesome-project
**主要语言**: Python (45 个文件)
**框架**: Django, Django REST Framework

## 🏗️ 项目结构
| 目录名称 | 文件数量 | 用途 |
|---------|---------|------|
| src      | 120      | 源代码 |
| tests    | 35       | 测试代码 |
| docs     | 8        | 文档 |

## 📊 VibeKit 深度分析
- ⚠️ 发现 2 处循环依赖
- ⚠️ 发现 1 个上帝模块

## 🚀 开发环境配置建议
[详细的工具链和优化建议]
```

### 退出代码
- `0`: 项目架构健康
- `1`: 发现架构问题，建议查看报告

---

## 9. analyze_existing_project.py

### 功能
VibeKit 核心分析引擎，深度分析项目的依赖关系和架构质量。

### 使用场景
- 手动运行深度架构分析
- 集成到 CI/CD 流程
- 定期架构健康检查

### 命令行
```bash
python project_team/skills/analyze_existing_project.py /path/to/project
```

### 核心算法
- **Tarjan 强连通分量**: O(V+E) 循环依赖检测
- **图论算法**: 依赖路径分析
- **复杂度度量**: 圈复杂度和认知复杂度

### 输出
- `.vibekit/analysis_report.md`: 详细分析报告
- `.vibekit/dependency_graph.svg`: 可视化依赖图
- `.vibekit/dependency_data.json`: 原始数据

---

## 10. generate_test_template.py

### 功能
为实现文件生成对应的测试模板。

### 使用场景
- Dev Mode 开始 TDD 前
- 需要为新文件创建测试
- 快速生成测试骨架

### 命令行
```bash
python skills/generate_test_template.py <impl_file> [framework]
```

### 输入
- `<impl_file>`: 实现文件路径 (如 "src/auth/api/login.py")
- `[framework]`: 测试框架 (默认 "pytest")
  - 支持: pytest, unittest, jest

### 输出
- 测试文件 (如 "tests/auth/api/test_login.py")

### 支持的测试框架

#### 1. pytest (Python,默认)
```python
# tests/auth/api/test_login.py
import pytest
from src.auth.api.login import login_handler, logout_handler

class TestLoginHandler:
    """测试 login_handler 函数"""

    def test_login_handler_success(self):
        """测试登录成功"""
        # TODO: 实现测试
        pass

    def test_login_handler_invalid_credentials(self):
        """测试无效凭证"""
        # TODO: 实现测试
        pass

class TestLogoutHandler:
    """测试 logout_handler 函数"""

    def test_logout_handler_success(self):
        """测试登出成功"""
        # TODO: 实现测试
        pass
```

#### 2. unittest (Python)
```python
# tests/auth/api/test_login.py
import unittest
from src.auth.api.login import login_handler

class TestLoginHandler(unittest.TestCase):
    """测试 login_handler 函数"""

    def test_login_success(self):
        """测试登录成功"""
        # TODO: 实现测试
        pass

if __name__ == '__main__':
    unittest.main()
```

#### 3. jest (JavaScript)
```javascript
// tests/auth/api/login.test.js
const { loginHandler, logoutHandler } = require('../../../src/auth/api/login');

describe('loginHandler', () => {
  test('should login successfully', () => {
    // TODO: 实现测试
  });

  test('should reject invalid credentials', () => {
    // TODO: 实现测试
  });
});
```

### 算法
1. 解析实现文件:
   - Python: 使用 AST 提取函数/类
   - JavaScript: 正则提取 export
2. 根据测试框架选择模板
3. 为每个符号生成测试骨架
4. 保存到对应的 tests/ 路径

### 示例

#### Python + pytest
```bash
# 实现文件: src/auth/api/login.py
async def login_handler(request):
    pass

async def logout_handler(request):
    pass

# 执行
python skills/generate_test_template.py src/auth/api/login.py pytest

# 输出
✓ 解析实现文件: src/auth/api/login.py
✓ 发现 2 个函数: login_handler, logout_handler
✓ 使用框架: pytest
✓ 生成测试文件: tests/auth/api/test_login.py
✓ 包含 4 个测试用例
```

#### JavaScript + jest
```bash
# 执行
python skills/generate_test_template.py src/auth/api/login.js jest

# 输出
✓ 解析实现文件: src/auth/api/login.js
✓ 发现 2 个 export: loginHandler, logoutHandler
✓ 使用框架: jest
✓ 生成测试文件: tests/auth/api/login.test.js
```

### 设计原则
- **符号驱动**: 根据实现文件的符号生成测试
- **多框架支持**: 支持主流测试框架
- **骨架生成**: 提供结构,具体测试由开发者填写

---

## Skill 使用工作流

### 完整开发流程中的 Skill 调用

```
Phase 1: Specify (PM Mode)
└── (无 Skill,手动编写 requirements.md)

Phase 2: Plan (Architect Mode)
├── build_main_index.py                    # 构建主索引
└── checkpoint.py save . plan              # 保存快照

Phase 3: Implement (Dev Mode)
├── build_module_index.py . auth           # 构建模块索引
├── generate_test_template.py src/auth/api/login.py pytest  # 生成测试
├── run_tdd_cycle.py . task_001            # 执行 TDD
│   ├── Red: 写测试 → FAIL
│   ├── Green: 写实现 → PASS
│   └── Refactor: 优化 → 仍然 PASS
├── search_in_module.py . auth find_symbol:User  # 查找符号
├── compress_context.py . task_001         # 压缩上下文
└── checkpoint.py save . implement_done    # 保存快照

Phase 4: Test (QA Mode)
└── checkpoint.py save . test_passed       # 保存快照

Phase 5: Release (Architect Mode)
└── checkpoint.py save . release           # 保存快照
```

## 设计原则总结

### 1. Agent vs Skill 边界
- **Agent**: 设计决策、流程控制、质量判断
- **Skill**: 自动化操作、重复任务、工具集成

### 2. 单一职责
每个 Skill 只做一件事:
- `build_main_index.py`: 只构建主索引
- `run_tdd_cycle.py`: 只执行 TDD 流程
- 不要让一个 Skill 承担多个职责

### 3. 可组合
Skill 之间可以组合使用:
```bash
# 先构建索引,再搜索
python build_module_index.py . auth
python search_in_module.py . auth find_symbol:User
```

### 4. 指针优先
- 输出指针而非完整内容
- 按需检索详细信息
- 减少上下文爆炸

### 5. JSON 输出
所有 Skill 输出 JSON 格式,便于:
- 程序解析
- 链式调用
- 持久化存储

## 参考

- **设计文档**: MyBrain/sessions/2025/12/session_004_detailed_summary.md
- **架构文档**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **智囊团**: Elon Musk, Martin Fowler, Charlie Munger, DHH, Uncle Bob
- **设计日期**: 2025-12-04

---

*Skills Reference v3.0 - Designed by MyBrain Technical Strategy Council*
