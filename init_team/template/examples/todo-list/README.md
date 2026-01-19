# TODO List API - 示例项目

> 使用 project-team-system v3.0 开发流程的完整示例

## 项目简介

这是一个使用 project-team-system 开发的 TODO List REST API 示例项目，展示完整的 v3.0 开发流程。

**功能**: 创建、查看、更新、删除 TODO 任务

**技术栈**:
- Web 框架: Flask/FastAPI
- 存储: 内存存储
- 测试: pytest + TDD

## 开发流程演示

本项目严格按照 project-team-system 的 5 个 Phase 进行开发。

### Phase 1: Specify (PM Mode) ✓

**角色**: PM Mode
**任务**: 需求分析和文档化

**输入**: 用户需求
**输出**: 完整的需求文档集

```bash
# 查看核心需求文档
cat requirements.md
cat docs/01_specify/prd.md
cat docs/01_specify/user_stories.md
cat docs/01_specify/api_spec.md
```

**强制文档**:
- `docs/01_specify/prd.md` - 产品需求文档
- `docs/01_specify/user_stories.md` - 用户故事清单
- `docs/01_specify/api_spec.md` - API 规范

**约束**:
- 必须完成所有文档才能进入下一阶段
- 用户故事必须包含验收标准
- API 规范必须完整无歧义

**包含**:
- 5 个 User Stories，每个都有明确的验收标准
- 完整的 REST API 规范
- 功能优先级排序
- 非功能性需求

**阶段完成**:
```bash
# 保存阶段快照
python ../../project_team/skills/checkpoint.py save . specify_complete
```

### Phase 2: Plan (Architect Mode)

**角色**: Architect Mode
**任务**: 架构设计和文档化

```bash
# 1. 构建主索引（强制）
python ../../project_team/skills/build_main_index.py .

# 2. 查看主索引
cat .context/main_index.json

# 3. 查看架构文档
cat docs/02_plan/architecture.md
cat docs/02_plan/module_design.md
cat docs/02_plan/database_design.md

# 4. 保存阶段快照
python ../../project_team/skills/checkpoint.py save . plan_complete
```

**强制文档**:
- `docs/02_plan/architecture.md` - 技术架构设计
- `docs/02_plan/module_design.md` - 模块设计方案
- `docs/02_plan/database_design.md` - 数据库设计
- `.context/main_index.json` - 项目主索引

**约束**:
- 必须构建主索引，系统自动验证
- 架构设计必须基于 PRD 和用户故事
- 每个模块必须有明确的职责边界

**架构决策**:
```
技术栈:
- 后端: Flask (Python)
- 数据存储: 内存存储 (可扩展到数据库)
- 测试: pytest

模块划分:
src/
├── api/         # REST API 层 - Flask 路由
├── models/      # 业务模型层 - Todo 类
└── storage/     # 数据存储层 - 内存存储
```

**输出**:
- 完整的架构设计文档
- 模块接口定义
- 数据库表结构
- `.context/main_index.json` (主索引)
- `.checkpoints/plan_complete_*.json` (快照)

### Phase 3: Implement (Dev Mode)

**角色**: Dev Mode
**任务**: TDD 开发各个模块

#### Task 001: 实现 Todo 模型

```bash
# 1. 构建模块索引
python ../../skills/build_module_index.py . models

# 2. 生成测试模板
python ../../skills/generate_test_template.py src/models/todo.py pytest

# 3. 执行 TDD 循环
python ../../skills/run_tdd_cycle.py . task_001
```

**TDD 流程**:
```
Red Phase:
  ✓ 编写测试 tests/models/test_todo.py
  ✓ 运行 pytest → FAIL (预期)

Green Phase:
  ✓ 实现 src/models/todo.py
  ✓ 运行 pytest → PASS

Refactor Phase:
  ✓ 优化代码结构 (可选)
  ✓ 运行 pytest → 仍然 PASS
```

#### Task 002: 实现内存存储

```bash
python ../../skills/build_module_index.py . storage
python ../../skills/generate_test_template.py src/storage/memory.py pytest
python ../../skills/run_tdd_cycle.py . task_002
```

#### Task 003: 实现 REST API

```bash
python ../../skills/build_module_index.py . api
python ../../skills/generate_test_template.py src/api/todos.py pytest
python ../../skills/run_tdd_cycle.py . task_003
```

#### 搜索和导航

```bash
# 列出 api 层的所有文件
python ../../skills/search_in_module.py . api list_files:api

# 查找某个函数定义
python ../../skills/search_in_module.py . api find_symbol:create_todo

# 读取完整文件
python ../../skills/search_in_module.py . api read_file:todos.py
```

### Phase 4: Test (QA Mode)

**角色**: QA Mode
**任务**: 集成测试，质量保证

```bash
# 1. 运行所有测试
pytest tests/ --cov --cov-report=term-missing

# 2. 检查覆盖率 (应该 > 80%)
# 3. 保存快照
python ../../skills/checkpoint.py save . test_passed
```

**质量标准**:
- ✅ 所有测试通过
- ✅ 测试覆盖率 > 80%
- ✅ 无未处理的错误

### Phase 5: Release (Architect Mode)

**角色**: Architect Mode
**任务**: 最终审查，发布准备

```bash
# 1. 最终代码审查
# 2. 更新文档
# 3. 保存 release 快照
python ../../skills/checkpoint.py save . release

# 4. 查看所有快照
python ../../skills/checkpoint.py list .
```

## 项目结构

```
todo-list/
├── .context/                    # 上下文索引
│   ├── main_index.json             # 主索引 (Architect 用)
│   └── modules/
│       ├── api_index.json          # API 模块索引
│       ├── models_index.json       # Models 模块索引
│       └── storage_index.json      # Storage 模块索引
├── .checkpoints/                # 状态快照
│   ├── plan_*.json                 # Plan 阶段快照
│   ├── implement_*.json            # Implement 阶段快照
│   ├── test_passed_*.json          # Test 阶段快照
│   └── release_*.json              # Release 快照
├── src/                         # 源代码
│   ├── api/
│   │   └── todos.py                # REST API 实现
│   ├── models/
│   │   └── todo.py                 # Todo 模型
│   └── storage/
│       └── memory.py               # 内存存储
├── tests/                       # 测试代码
│   ├── api/
│   │   └── test_todos.py           # API 测试
│   ├── models/
│   │   └── test_todo.py            # 模型测试
│   └── storage/
│       └── test_memory.py          # 存储测试
├── .project_state.json          # 项目状态
├── sop.yaml                     # 开发流程
├── requirements.md              # 需求文档
└── README.md                    # 本文件
```

## 学习要点

### 1. 分层索引的使用

**Architect 视角** (模块级):
```json
// .context/main_index.json
{
  "modules": {
    "api": { "purpose": "REST API 层", "layers": [] },
    "models": { "purpose": "业务模型", "layers": [] },
    "storage": { "purpose": "数据存储", "layers": [] }
  }
}
```

**Dev 视角** (文件级):
```json
// .context/modules/api_index.json
{
  "files": [
    {
      "path": "src/api/todos.py",
      "exports": ["create_todo", "get_todos", "get_todo", "update_todo", "delete_todo"]
    }
  ]
}
```

### 2. 指针式上下文

**传统方式** (上下文爆炸):
```python
# 传递完整代码 (500 行)
context = {
    "todos.py": "<完整的 500 行代码>"
}
```

**指针式** (轻量级):
```python
# 传递指针和预览
context = {
    "pointer": "src/api/todos.py#create_todo",
    "preview": "def create_todo(title, description):\n    ...",
    "on_demand": True
}
```

### 3. 严格 TDD

本项目展示严格的 TDD 流程:
- **Red**: 先写测试，必须失败
- **Green**: 写最小实现，通过测试
- **Refactor**: 可选优化

每个功能都遵循这个循环，确保代码质量。

### 4. Skill 的使用时机

| Phase | Role | Skill |
|-------|------|-------|
| Specify | PM | (无，手动编写) |
| Plan | Architect | build_main_index.py, checkpoint.py |
| Implement | Dev | build_module_index.py, generate_test_template.py, run_tdd_cycle.py, search_in_module.py |
| Test | QA | checkpoint.py |
| Release | Architect | checkpoint.py |

## API 文档

### 创建任务
```bash
POST /api/todos
Content-Type: application/json

{
  "title": "学习 Python",
  "description": "完成基础教程"
}
```

### 查看所有任务
```bash
GET /api/todos?status=pending
```

### 查看单个任务
```bash
GET /api/todos/:id
```

### 更新任务
```bash
PUT /api/todos/:id
Content-Type: application/json

{
  "status": "completed"
}
```

### 删除任务
```bash
DELETE /api/todos/:id
```

## 运行项目

```bash
# 安装依赖
pip install flask pytest pytest-cov

# 运行测试
pytest tests/ --cov

# 启动服务
python src/api/todos.py

# 测试 API
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "测试任务"}'
```

## 参考资料

- **系统文档**: ../../README.md
- **架构设计**: ../../docs/ARCHITECTURE.md
- **Skills 参考**: ../../docs/SKILLS.md
- **需求文档**: requirements.md
- **SOP 流程**: sop.yaml

## 下一步

1. **实践**: 按照 Phase 2-5 完成项目开发
2. **理解**: 体验 Architect 和 Dev 两种视角的切换
3. **学习**: 掌握 TDD 工作流和 Skill 的使用
4. **扩展**: 尝试添加新功能 (如任务优先级、截止日期)

---

*示例项目 - project-team-system v3.0*