# TODO List API 需求文档

版本: 1.0.0

## 项目概述

构建一个简单但完整的 REST API，用于管理 TODO 任务列表。

本示例项目展示如何使用 project-team-system 开发流程:
- Phase 1 (Specify): 本文档
- Phase 2 (Plan): 使用 build_main_index.py 构建架构
- Phase 3 (Implement): 使用 TDD 流程开发
- Phase 4 (Test): 集成测试
- Phase 5 (Release): 发布

## User Stories

### US-001: 创建任务
**作为** 用户
**我希望** 能够创建新的 TODO 任务
**以便** 记录我需要完成的事项

**验收标准**:
- 提供 POST /api/todos 接口
- 请求 body: `{ "title": "任务标题", "description": "任务描述" }`
- 返回创建的任务 (包含自动生成的 ID 和时间戳)
- 标题为必填项，描述可选
- 新任务默认状态为 "pending"

**示例**:
```json
// POST /api/todos
{
  "title": "学习 Python",
  "description": "完成 Python 基础教程第 3 章"
}

// Response 201 Created
{
  "id": "todo_001",
  "title": "学习 Python",
  "description": "完成 Python 基础教程第 3 章",
  "status": "pending",
  "created_at": "2024-12-04T10:00:00Z",
  "updated_at": "2024-12-04T10:00:00Z"
}
```

### US-002: 查看所有任务
**作为** 用户
**我希望** 能够查看所有任务列表
**以便** 了解我的待办事项

**验收标准**:
- 提供 GET /api/todos 接口
- 返回所有任务列表
- 支持按状态筛选: `?status=pending|completed`
- 按创建时间倒序排列 (最新的在前)

**示例**:
```json
// GET /api/todos?status=pending

// Response 200 OK
{
  "todos": [
    {
      "id": "todo_002",
      "title": "写报告",
      "description": "",
      "status": "pending",
      "created_at": "2024-12-04T11:00:00Z",
      "updated_at": "2024-12-04T11:00:00Z"
    },
    {
      "id": "todo_001",
      "title": "学习 Python",
      "description": "完成 Python 基础教程第 3 章",
      "status": "pending",
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    }
  ],
  "total": 2
}
```

### US-003: 查看单个任务
**作为** 用户
**我希望** 能够查看单个任务的详细信息
**以便** 了解任务的具体内容

**验收标准**:
- 提供 GET /api/todos/:id 接口
- 返回指定 ID 的任务
- 如果任务不存在，返回 404

**示例**:
```json
// GET /api/todos/todo_001

// Response 200 OK
{
  "id": "todo_001",
  "title": "学习 Python",
  "description": "完成 Python 基础教程第 3 章",
  "status": "pending",
  "created_at": "2024-12-04T10:00:00Z",
  "updated_at": "2024-12-04T10:00:00Z"
}
```

### US-004: 更新任务
**作为** 用户
**我希望** 能够更新任务的内容或状态
**以便** 修改或标记任务完成

**验收标准**:
- 提供 PUT /api/todos/:id 接口
- 可更新 title, description, status
- 更新时自动更新 updated_at
- 如果任务不存在，返回 404

**示例**:
```json
// PUT /api/todos/todo_001
{
  "status": "completed"
}

// Response 200 OK
{
  "id": "todo_001",
  "title": "学习 Python",
  "description": "完成 Python 基础教程第 3 章",
  "status": "completed",
  "created_at": "2024-12-04T10:00:00Z",
  "updated_at": "2024-12-04T15:00:00Z"
}
```

### US-005: 删除任务
**作为** 用户
**我希望** 能够删除任务
**以便** 移除不需要的任务

**验收标准**:
- 提供 DELETE /api/todos/:id 接口
- 成功删除返回 204 No Content
- 如果任务不存在，返回 404

**示例**:
```json
// DELETE /api/todos/todo_001

// Response 204 No Content
```

## 技术要求

### 架构设计
使用分层架构:
```
src/
├── api/         # API 层 - REST 接口
│   └── todos.py
├── models/      # 模型层 - 数据结构
│   └── todo.py
└── storage/     # 存储层 - 数据持久化
    └── memory.py
```

### 技术栈
- **Web 框架**: Flask 或 FastAPI
- **数据存储**: 内存存储 (字典) - 简单起见
- **测试框架**: pytest
- **代码风格**: PEP 8

### 数据模型
```python
class Todo:
    id: str                    # 唯一标识
    title: str                 # 标题 (必填)
    description: str           # 描述 (可选)
    status: str                # 状态: pending | completed
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

## 非功能性需求

### 性能
- 所有 API 响应时间 < 100ms (内存存储)
- 支持至少 1000 个任务

### 质量
- 测试覆盖率 > 80%
- 所有 API 必须有对应测试
- 遵循 TDD 流程: Red → Green → Refactor

### 错误处理
- 标题为空: 400 Bad Request
- 任务不存在: 404 Not Found
- 无效的状态值: 400 Bad Request

### API 规范
- RESTful 风格
- JSON 格式请求和响应
- 正确的 HTTP 状态码

## 开发流程 (使用 project-team-system)

### Phase 1: Specify ✓
- 本文档

### Phase 2: Plan (Architect Mode)
```bash
# 构建主索引
python ../skills/build_main_index.py .

# 保存快照
python ../skills/checkpoint.py save . plan
```

**架构决策**:
1. 3 个模块: api, models, storage
2. 使用 Flask (轻量级)
3. 内存存储 (简单快速)

### Phase 3: Implement (Dev Mode)

#### 3.1 模块: models
**任务**: 实现 Todo 数据模型

```bash
# 构建模块索引
python ../skills/build_module_index.py . models

# 生成测试模板
python ../skills/generate_test_template.py src/models/todo.py pytest

# TDD 开发
python ../skills/run_tdd_cycle.py . task_001
```

#### 3.2 模块: storage
**任务**: 实现内存存储

```bash
python ../skills/build_module_index.py . storage
python ../skills/generate_test_template.py src/storage/memory.py pytest
python ../skills/run_tdd_cycle.py . task_002
```

#### 3.3 模块: api
**任务**: 实现 REST API

```bash
python ../skills/build_module_index.py . api
python ../skills/generate_test_template.py src/api/todos.py pytest
python ../skills/run_tdd_cycle.py . task_003
```

### Phase 4: Test (QA Mode)
```bash
# 运行所有测试
pytest tests/ --cov

# 保存快照
python ../skills/checkpoint.py save . test_passed
```

### Phase 5: Release (Architect Mode)
```bash
# 最终审查
# 更新 README
# 保存快照
python ../skills/checkpoint.py save . release
```

## 测试用例清单

### 模型测试 (tests/models/test_todo.py)
- [ ] test_create_todo_with_title
- [ ] test_create_todo_with_title_and_description
- [ ] test_create_todo_without_title_raises_error
- [ ] test_todo_default_status_is_pending
- [ ] test_update_todo_status
- [ ] test_todo_to_dict

### 存储测试 (tests/storage/test_memory.py)
- [ ] test_create_todo_returns_id
- [ ] test_get_todo_by_id
- [ ] test_get_nonexistent_todo_returns_none
- [ ] test_list_all_todos
- [ ] test_list_todos_by_status
- [ ] test_update_todo
- [ ] test_delete_todo

### API 测试 (tests/api/test_todos.py)
- [ ] test_post_create_todo_success
- [ ] test_post_create_todo_without_title_400
- [ ] test_get_list_todos_success
- [ ] test_get_list_todos_filter_by_status
- [ ] test_get_todo_by_id_success
- [ ] test_get_todo_by_id_not_found_404
- [ ] test_put_update_todo_success
- [ ] test_put_update_todo_not_found_404
- [ ] test_delete_todo_success
- [ ] test_delete_todo_not_found_404

## 参考

- **开发系统**: project-team-system v3.0
- **架构文档**: ../docs/ARCHITECTURE.md
- **Skills 参考**: ../docs/SKILLS.md

---

*需求文档 v1.0 - 用于展示 project-team-system 工作流程*
