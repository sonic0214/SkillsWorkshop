# Project Team System

v6.0 - Complexity-Adaptive Development Framework

> 外部项目开发团队系统 - 基于 session_004 设计，经技术战略智囊团讨论达成共识

## 🆕 v6.0 新特性

**三级 SOP 模式 + 复杂度自适应**：
- Fast Track: MVP/原型验证（简化流程）
- Standard: 常规业务系统（推荐默认）
- Rigorous: 关键业务/生产环境（严格质量控制）
- 自动评估项目复杂度，推荐合适的流程模式
- 超时处理机制，避免用户离线时系统阻塞
- 智囊团自动触发规则，主动质量控制

## v3.1 特性（保留）

**项目代码与框架完全分离**：
- 框架位于 `project_team/` 目录
- 项目代码独立组织，避免污染
- 清晰的职责边界和更好的可维护性

## Quick Start

```bash
# Create new project
python skills/create_project_structure.py my-project

# Enter project
cd my-project

# Edit requirements
vim requirements.md

# Build main index (Architect mode)
python ../skills/build_main_index.py .

# Run TDD cycle (Dev mode)
python ../skills/run_tdd_cycle.py . task_001
```

## Core Concepts

### 1. Single Agent + 4 Role Modes
One Project Agent switches between 4 roles:
- **PM Mode**: Requirements analysis, user stories
- **Architect Mode**: Architecture design, module navigation (forest view)
- **Dev Mode**: TDD development, code implementation (tree view)
- **QA Mode**: Integration testing, quality assurance

### 2. Layered Indexing
- **Main index** (`.context/main_index.json`): Module-level, for Architect
- **Module index** (`.context/modules/{module}_index.json`): File-level, for Dev
- **Principle**: Architect sees forest, Dev sees trees

### 3. Agent vs Skill Boundary
- **Agent**: Design decisions, flow control, quality judgment (non-automatable)
- **Skill**: Automation operations, repetitive tasks, tool integration (automatable)

### 4. Pointer-based Context
- Pass pointers (file_path#section), not full content
- Retrieve on demand
- Avoid context explosion

### 5. Strict TDD
- **Red**: Write test, must fail
- **Green**: Write code, test must pass
- **Refactor**: Optional optimization

## Directory Structure

### 开发实例（使用 init_team 创建）

```
my-dev-system/                     # 开发实例（v6.0）
├── project_team/                   # 框架目录（只读）
│   ├── skills/                    # 开发技能脚本
│   │   ├── build_main_index.py
│   │   ├── build_module_index.py
│   │   ├── search_in_module.py
│   │   ├── compress_context.py
│   │   ├── run_tdd_cycle.py
│   │   ├── checkpoint.py
│   │   ├── create_project_structure.py
│   │   ├── generate_test_template.py
│   │   ├── assess_complexity.py   # v6.0: 复杂度评估
│   │   └── validate_phase_gate.py
│   ├── agents/                    # Agent 定义
│   │   ├── project_agent.md       # 主 Agent
│   │   ├── project_manager.md     # 项目经理
│   │   ├── council_integration.md # 智囊团集成
│   │   └── roles/                 # 角色模式详细定义
│   │       ├── pm_mode.md
│   │       ├── architect_mode.md
│   │       ├── dev_mode.md
│   │       └── qa_mode.md
│   ├── sop_templates/             # v6.0: SOP 模板库
│   │   ├── sop_fast_track.yaml
│   │   ├── sop_standard.yaml
│   │   └── sop_rigorous.yaml
│   ├── examples/                  # 学习示例
│   │   └── todo-list/
│   ├── docs/                      # 框架文档
│   │   ├── ARCHITECTURE.md
│   │   └── SKILLS.md
│   ├── constraints/               # 约束文档
│   │   └── documentation_constraints.md
│   └── README.md                  # 框架说明（本文件）
│
├── sop.yaml                       # v6.0: 项目 SOP（从模板复制）
├── requirements.md                # 项目需求（可选）
├── .project_state.json            # 项目状态
├── CLAUDE.md                      # Project Agent 启动指南
├── README.md                      # 项目使用指南
└── .gitignore                     # Git 忽略
```

## Skill Scripts

### 1. build_main_index.py
Build project main index (module-level)
```bash
python skills/build_main_index.py <project_root>
```

### 2. build_module_index.py
Build module index (file-level)
```bash
python skills/build_module_index.py <project_root> <module_name>
```

### 3. search_in_module.py
Search in module
```bash
python skills/search_in_module.py <project_root> <module> list_files:api
python skills/search_in_module.py <project_root> <module> find_symbol:<name>
python skills/search_in_module.py <project_root> <module> read_file:api/login.py
```

### 4. compress_context.py
Compress task context
```bash
python skills/compress_context.py <project_root> <task_id>
```

### 5. run_tdd_cycle.py
Execute TDD workflow
```bash
python skills/run_tdd_cycle.py <project_root> <task_id>
```

### 6. checkpoint.py
Checkpoint management
```bash
python skills/checkpoint.py save <project_root> <phase_name>
python skills/checkpoint.py list <project_root>
```

### 7. create_project_structure.py
Create project structure
```bash
python skills/create_project_structure.py <project_name> [target_dir]
```

### 8. generate_test_template.py
Generate test template
```bash
python skills/generate_test_template.py <impl_file> [framework]
# Frameworks: pytest, unittest, jest
```

### 9. assess_complexity.py (v6.0)
Assess project complexity and recommend SOP mode
```bash
python skills/assess_complexity.py --requirements <requirements.md>
python skills/assess_complexity.py  # Interactive mode
```

### 10. validate_phase_gate.py
Validate phase gate requirements
```bash
python skills/validate_phase_gate.py <project_root> <from_phase> <to_phase>
```

## Creating New Instances (v6.0)

Create new instances using MyBrain with complexity-adaptive SOP:

```bash
# From MyBrain - Auto assess complexity
cd ~/Project/MyBrain
python skills/init_team/create.py \
    --target ~/new-project \
    --requirements handoff/requirements.md
# System will auto-assess complexity and recommend SOP mode

# Manual mode selection
python skills/init_team/create.py \
    --target ~/my-mvp \
    --mode fast_track  # or standard / rigorous

# Blank project (default: standard)
python skills/init_team/create.py --target ~/new-project
```

## Workflow Example

1. **Specify** (PM Mode)
   ```bash
   vim requirements.md  # Write requirements
   ```

2. **Plan** (Architect Mode)
   ```bash
   python skills/build_main_index.py .  # Build main index
   python skills/checkpoint.py save . plan  # Save checkpoint
   ```

3. **Implement** (Dev Mode)
   ```bash
   python skills/build_module_index.py . auth  # Build module index
   python skills/generate_test_template.py src/auth/api/login.py pytest
   python skills/run_tdd_cycle.py . task_001  # Run TDD
   ```

4. **Test** (QA Mode)
   ```bash
   pytest tests/  # Run integration tests
   python skills/checkpoint.py save . test  # Save checkpoint
   ```

5. **Release** (Architect Mode)
   ```bash
   # Final review and release
   ```

## Design Source

- **MyBrain session_004**: External project development team system design (v3.0)
- **MyBrain session_011**: Complexity-adaptive SOP modes (v6.0)
- **Council meeting_004**: Technical strategy council discussion
- **Design versions**: v3.0 → v3.1 → v6.0
- **Participants**: Elon Musk, Martin Fowler, Charlie Munger, DHH, Uncle Bob

## Key Insights

- **insight_011**: Layered indexing - Architect sees forest (module-level), Dev sees trees (file-level)
- **insight_012**: Pointer-based context - Pass pointers, retrieve on demand
- **insight_013**: Agent vs Skill boundary - Agent does design, Skill does automation

## Documentation

- [Architecture Design](docs/ARCHITECTURE.md)
- [Skills Reference](docs/SKILLS.md)

## License

MIT

---
*Created by: MyBrain/skills/init_team/create.py*
*Design: session_004 v3.0*
*Date: 2025-12-04*
