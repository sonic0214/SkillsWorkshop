# Project Team System - Architecture Design

v3.0 - Single Agent + Role Modes Architecture

> 设计来源: MyBrain session_004, 技术战略智囊团 meeting_004

## 核心理念

### 1. 单 Agent + 4 种角色模式

**设计决策**: 使用一个 Project Agent,通过切换角色模式完成不同职责

```
Project Agent
├── PM Mode      - 需求分析、用户故事
├── Architect Mode - 架构设计、模块导航 (森林视角)
├── Dev Mode     - TDD 开发、代码实现 (树木视角)
└── QA Mode      - 集成测试、质量保证
```

**优势**:
- 上下文连续性: 同一个 Agent,记忆完整
- 流程自然切换: 不需要复杂的通信协议
- 简化协作: 角色转换比多 Agent 通信更简单

**vs v1.0 (多 Agent 模式)**:
- v1.0: PM → Architect → Lead Dev → Dev (链式通信)
- v3.0: 单 Agent 切换角色 (内部状态切换)
- 原因: 在实际使用中,链式通信开销大,上下文易丢失

### 2. 分层索引系统

**insight_011**: "Architect 看森林 (模块级),Dev 看树木 (文件级)"

```
.context/
├── main_index.json              # 主索引 (模块级,给 Architect)
│   └── modules:
│       ├── auth/                # 模块信息
│       │   ├── purpose         # 模块用途
│       │   ├── layers          # 分层结构
│       │   └── module_index    # 指向详细索引
│       └── ...
└── modules/
    └── auth_index.json          # 模块索引 (文件级,给 Dev)
        └── files:
            ├── api/login.py    # 文件导出符号
            ├── models/user.py
            └── ...
```

**职责分离**:
- **Architect Mode**: 读取 main_index.json
  - 查看模块布局
  - 设计模块交互
  - 决定技术栈
  - 复杂度 O(m),m = 模块数量

- **Dev Mode**: 读取 {module}_index.json
  - 查看文件列表
  - 搜索符号定义
  - 按需读取文件
  - 复杂度 O(f),f = 模块内文件数

**为什么分层**:
- 防止上下文爆炸: Architect 不需要看到所有文件
- 按需加载: Dev 只加载当前模块
- 清晰职责: 不同角色看到不同粒度

### 3. Agent vs Skill 边界

**insight_013**: "Agent 做设计决策,Skill 做自动化操作"

```
┌─────────────────────────────────────────────┐
│ Agent (非自动化,需要智能)                    │
├─────────────────────────────────────────────┤
│ - 架构决策 (选择技术栈)                      │
│ - 质量判断 (代码是否需要重构)                │
│ - 流程控制 (决定下一步做什么)                │
│ - 需求理解 (将用户故事转化为任务)            │
└─────────────────────────────────────────────┘
                    ▼
          调用 Skill (自动化)
                    ▼
┌─────────────────────────────────────────────┐
│ Skill (可自动化,可重复)                      │
├─────────────────────────────────────────────┤
│ - 构建索引 (build_main_index.py)            │
│ - 执行测试 (run_tdd_cycle.py)               │
│ - 管理快照 (checkpoint.py)                  │
│ - 生成模板 (generate_test_template.py)     │
└─────────────────────────────────────────────┘
```

**判断标准**:
- 如果操作可以写成脚本 → Skill
- 如果需要判断和决策 → Agent
- 如果是重复性任务 → Skill
- 如果每次都不同 → Agent

**示例**:
- "构建模块索引" → Skill (固定算法)
- "决定是否重构" → Agent (需要判断)
- "生成测试模板" → Skill (模板固定)
- "设计 API 接口" → Agent (创造性工作)

### 4. 指针式上下文传递

**insight_012**: "传递指针 (file_path#section),而非完整内容"

**传统方式** (上下文爆炸):
```python
context = {
    "auth_api": "<完整的 500 行代码>",
    "user_model": "<完整的 300 行代码>",
    # ... 10 个文件 = 5000 行上下文
}
```

**指针式** (按需检索):
```python
context = {
    "auth_api": {
        "pointer": "src/auth/api/login.py#login_handler",
        "preview": "async def login_handler(request):\n    # 处理登录请求\n    ...",
        "on_demand": True
    }
}
```

**工作流程**:
1. Architect 创建任务,包含指针列表
2. Dev 读取指针预览,判断是否需要完整内容
3. 如需要,调用 `search_in_module.py read_file:path` 检索
4. 避免一次性加载所有代码

**好处**:
- 上下文从 5000 行降到 50 行 (预览)
- 99% 情况下预览足够
- 需要时 O(1) 检索完整内容

### 5. 严格 TDD 工作流

**Red → Green → Refactor**

```
┌─────────────────────────────────────────┐
│ Red Phase (必须失败)                     │
├─────────────────────────────────────────┤
│ 1. 写测试 (test_login.py)               │
│ 2. 运行 pytest → 必须 FAIL              │
│ 3. 如果 PASS → 测试无效,重写             │
└─────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│ Green Phase (通过测试)                   │
├─────────────────────────────────────────┤
│ 1. 写最小实现 (login.py)                 │
│ 2. 运行 pytest → 必须 PASS              │
│ 3. 如果 FAIL → 继续实现                 │
└─────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│ Refactor Phase (可选)                   │
├─────────────────────────────────────────┤
│ 1. 优化代码结构                          │
│ 2. 运行 pytest → 仍然 PASS              │
└─────────────────────────────────────────┘
```

**为什么严格**:
- Red 必须失败: 确保测试有效
- Green 先通过: 避免过度设计
- Refactor 可选: 不强制优化

**Skill 支持**:
- `run_tdd_cycle.py`: 自动执行 Red → Green → Refactor
- `generate_test_template.py`: 生成测试模板
- 保证流程不被跳过

### 6. SOP 文件驱动流程

**设计**: 将开发流程定义在 sop.yaml,而非硬编码

```yaml
phases:
  specify:
    description: "需求分析"
    role: "PM"
    input: "requirements.md"
    output: ".context/user_stories.json"
    skills: []

  plan:
    description: "架构设计"
    role: "Architect"
    input: ".context/user_stories.json"
    output: ".context/main_index.json"
    skills:
      - build_main_index.py

  implement:
    description: "TDD 开发"
    role: "Dev"
    input: ".context/tasks/*.json"
    output: "src/**, tests/**"
    skills:
      - build_module_index.py
      - run_tdd_cycle.py
      - generate_test_template.py
```

**好处**:
- 流程可自定义: 不同项目不同 SOP
- Agent 读取 SOP: 根据当前 phase 选择角色
- 可追溯: 每个 phase 输入输出明确

## 目录结构

### project-team-system (系统本体)

```
project-team-system/
├── skills/                     # 8 个 Skill 脚本
│   ├── build_main_index.py         # 构建主索引
│   ├── build_module_index.py       # 构建模块索引
│   ├── search_in_module.py         # 模块内搜索
│   ├── compress_context.py         # 压缩上下文
│   ├── run_tdd_cycle.py            # 执行 TDD 流程
│   ├── checkpoint.py               # 快照管理
│   ├── create_project_structure.py # 创建项目
│   └── generate_test_template.py   # 生成测试模板
├── agents/
│   └── project_agent.md            # Agent 定义 (4 种角色)
├── project_template/               # 项目模板
│   ├── .context/                   # 索引目录
│   ├── .checkpoints/               # 快照目录
│   ├── sop.yaml                    # 流程定义
│   ├── requirements.md             # 需求文档
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md             # 本文件
│   └── SKILLS.md                   # Skill 参考
└── README.md
```

### 使用系统创建的项目

```
my-project/                     # 从 project_template/ 创建
├── .context/
│   ├── main_index.json             # 主索引 (Architect 用)
│   └── modules/
│       └── auth_index.json         # 模块索引 (Dev 用)
├── .checkpoints/
│   ├── plan_20241204.json          # 快照
│   └── implement_20241204.json
├── src/                            # 源代码
│   └── auth/
│       ├── api/
│       └── models/
├── tests/                          # 测试代码
│   └── auth/
├── sop.yaml                        # 流程定义
├── requirements.md                 # 需求文档
└── .project_state.json             # 项目状态
```

## 工作流程

### 完整流程示例: 开发登录功能

#### Phase 1: Specify (PM Mode)

**输入**: 用户需求
**角色**: PM Mode
**操作**:
```bash
vim requirements.md
```

```markdown
# 需求: 用户登录

## User Story
作为用户,我希望能够通过邮箱和密码登录系统,以访问个人数据。

## 验收标准
- 提供 POST /api/auth/login 接口
- 验证邮箱格式
- 验证密码强度
- 返回 JWT token
```

**输出**: requirements.md

#### Phase 2: Plan (Architect Mode)

**输入**: requirements.md
**角色**: Architect Mode
**操作**:
```bash
python ../skills/build_main_index.py .
python ../skills/checkpoint.py save . plan
```

**决策**:
- 模块划分: auth/ (认证模块)
- 技术栈: FastAPI + JWT
- 分层结构: api/ (接口), models/ (数据), services/ (业务)

**输出**: .context/main_index.json
```json
{
  "modules": {
    "auth": {
      "purpose": "用户认证",
      "layers": ["api", "models", "services"],
      "module_index": ".context/modules/auth_index.json"
    }
  }
}
```

#### Phase 3: Implement (Dev Mode)

**输入**: .context/main_index.json, task_001.json
**角色**: Dev Mode

**Step 1**: 构建模块索引
```bash
python ../skills/build_module_index.py . auth
```

**Step 2**: 生成测试模板
```bash
python ../skills/generate_test_template.py src/auth/api/login.py pytest
# 生成 tests/auth/api/test_login.py
```

**Step 3**: TDD 开发
```bash
python ../skills/run_tdd_cycle.py . task_001
```

**TDD 详细流程**:
```
Red Phase:
  ✓ 编写测试 tests/auth/api/test_login.py
    - test_login_success()
    - test_login_invalid_email()
    - test_login_wrong_password()

  ✓ 运行 pytest → FAIL (预期)
    - login_handler 函数不存在

Green Phase:
  ✓ 实现 src/auth/api/login.py
    async def login_handler(request):
        email = request.json["email"]
        password = request.json["password"]
        # 验证逻辑
        return {"token": generate_jwt(user)}

  ✓ 运行 pytest → PASS

Refactor Phase:
  ✓ 提取验证逻辑到 services/auth_service.py
  ✓ 运行 pytest → 仍然 PASS
```

**输出**: src/auth/**, tests/auth/**

#### Phase 4: Test (QA Mode)

**输入**: 完整代码
**角色**: QA Mode
**操作**:
```bash
pytest tests/ --cov
python ../skills/checkpoint.py save . test_passed
```

**输出**: 测试报告, checkpoint

#### Phase 5: Release (Architect Mode)

**输入**: 测试通过的代码
**角色**: Architect Mode
**操作**:
- 最终审查
- 更新文档
- 创建 release checkpoint

## 设计演进

### v1.0 → v3.0 的变化

| 方面 | v1.0 (多 Agent) | v3.0 (单 Agent + 角色) |
|------|----------------|----------------------|
| 架构 | PM → Architect → Lead Dev → Dev | 单 Agent 切换 4 种角色 |
| 协作 | 链式通信,上下文易丢失 | 内部状态切换,上下文连续 |
| 索引 | 单层全局索引 | 分层索引 (main + module) |
| 上下文 | 传递完整内容 | 指针式按需检索 |
| 复杂度 | 高 (4 个 Agent 通信) | 低 (角色切换) |

### 关键洞察

**insight_011**: 分层索引
- Architect 看森林 (模块级,O(m))
- Dev 看树木 (文件级,O(f))
- 避免上下文爆炸

**insight_012**: 指针式上下文
- 传递 `file_path#section` 而非完整内容
- 按需检索,减少 99% 上下文

**insight_013**: Agent vs Skill 边界
- Agent: 设计决策、流程控制、质量判断
- Skill: 自动化操作、重复任务、工具集成

## 技术选型

### 索引构建
- 使用 Python AST 解析导出符号
- JSON 格式存储索引
- O(n) 扫描复杂度,n = 文件数

### 测试框架
- Python: pytest (默认)
- JavaScript: jest
- 支持自定义框架

### 快照管理
- JSON 格式存储状态
- 包含上下文指针 (不存储完整内容)
- 增量快照

### 系统创建
- `MyBrain/skills/init_team/create.py`: 从 MyBrain 创建新实例
- 使用 `shutil.copytree()` 复制完整目录树

## 设计原则

1. **简单胜于复杂**: 单 Agent 优于多 Agent
2. **按需加载**: 指针式上下文,避免爆炸
3. **职责分离**: Architect 看森林,Dev 看树木
4. **流程严格**: TDD 必须 Red → Green
5. **可配置**: SOP 文件驱动流程
6. **可复制**: 系统自举能力

## 参考

- **设计文档**: MyBrain/sessions/2025/12/session_004_detailed_summary.md
- **会议记录**: MyBrain/council/meetings/2025/meeting_004_project_team_design.md
- **智囊团**: Elon Musk, Martin Fowler, Charlie Munger, DHH, Uncle Bob
- **设计日期**: 2025-12-04

---

*Architecture v3.0 - Designed by MyBrain Technical Strategy Council*
