#!/usr/bin/env python3
"""
VibeKit - init_new_project.py

功能: 初始化新项目结构
- 在 project_team 同级目录创建新项目
- 基于 project_template/ 目录模板
- 复制模板文件并替换变量
- 初始化 Git 仓库

使用:
    python project_team/skills/init_new_project.py <project_name> [target_dir]

触发条件:
    - Agent 检测到空项目目录
    - 询问用户是否初始化新项目
    - 用户确认后执行此脚本

设计:
    使用 project_template/ 作为模板，避免硬编码
    与 project_team/ 同级目录，便于管理
"""

import json
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from string import Template


def get_template_dir() -> Path:
    """获取模板目录"""
    # 脚本在 project_team/skills/ 目录，模板在 ../project_template/
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / "project_template"

    if not template_dir.exists():
        raise FileNotFoundError(f"模板目录不存在: {template_dir}")

    return template_dir


def get_project_team_root() -> Path:
    """获取 project_team 根目录"""
    # 脚本在 project_team/skills/ 目录，向上两级
    return Path(__file__).parent.parent


def create_doc_templates(target_dir: Path):
    """创建基础文档模板"""

    # 01_specify 阶段文档
    prd_template = """# 产品需求文档 (PRD)

## 项目概述
- 项目名称：{project_name}
- 版本：v1.0.0
- 创建日期：{date}
- 产品经理：[待填写]

## 需求背景
[描述项目背景和要解决的问题]

## 目标用户
[描述目标用户群体]

## 核心功能
### 功能 1：[功能名称]
- 用户故事：[作为...，我希望...，以便...]
- 优先级：高/中/低
- 验收标准：[如何验收]

### 功能 2：[功能名称]
- 用户故事：[作为...，我希望...，以便...]
- 优先级：高/中/低
- 验收标准：[如何验收]

## 非功能性需求
- 性能要求：
- 安全要求：
- 兼容性要求：

## 发布计划
- MVP 版本：[日期]
- v1.0 版本：[日期]
"""

    user_stories_template = """# 用户故事清单

## 用户故事列表

### Epic 1：[史诗名称]
#### Story 1：[故事名称]
**作为** [用户角色]，**我希望** [功能描述]，**以便** [价值/目的]。
- **优先级**：高/中/低
- **验收标准**：
  - Given [前置条件]
  - When [操作]
  - Then [预期结果]
- **估算**：[故事点]

#### Story 2：[故事名称]
**作为** [用户角色]，**我希望** [功能描述]，**以便** [价值/目的]。
- **优先级**：高/中/低
- **验收标准**：
  - Given [前置条件]
  - When [操作]
  - Then [预期结果]
- **估算**：[故事点]

### Epic 2：[史诗名称]
[继续添加...]

## 定义完成 (Definition of Done)
- [ ] 代码完成并通过测试
- [ ] 文档更新
- [ ] 代码审查通过
- [ ] 集成测试通过
"""

    api_spec_template = """# API 规范文档

## 概述
- API 版本：v1.0.0
- 基础 URL：`https://api.example.com/v1`
- 认证方式：[描述认证方式]

## 通用响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "code": 200
}
```

## API 端点

### 1. 用户管理

#### 1.1 创建用户
**POST** `/users`

**请求体**：
```json
{
  "name": "用户名",
  "email": "user@example.com",
  "password": "password"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "用户名",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 1.2 获取用户列表
**GET** `/users`

**查询参数**：
- `page`: 页码（默认 1）
- `limit`: 每页数量（默认 20）
- `search`: 搜索关键词

[继续添加其他 API...]

## 错误码
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 资源不存在
- `500`: 服务器内部错误
"""

    # 02_plan 阶段文档
    architecture_template = """# 技术架构设计

## 系统架构概览

### 架构模式
[选择：分层架构 / 微服务架构 / 事件驱动架构]

### 技术栈选择

#### 前端
- 框架：[React/Vue/Angular]
- 状态管理：[Redux/Vuex/MobX]
- UI 库：[Ant Design/Element UI/Material-UI]
- 构建工具：[Webpack/Vite]

#### 后端
- 语言：[Python/Java/Node.js]
- 框架：[Django/Spring Boot/Express]
- 数据库：[PostgreSQL/MySQL/MongoDB]
- 缓存：[Redis/Memcached]
- 消息队列：[RabbitMQ/Kafka]

#### 基础设施
- 容器化：Docker
- 编排：Kubernetes/Docker Compose
- 监控：[Prometheus/Grafana]
- 日志：[ELK Stack]

## 系统模块设计

### 模块划分
1. **用户模块** (User Module)
   - 注册、登录、个人信息管理
   - 权限控制

2. **业务模块** (Business Module)
   - [核心业务逻辑]

3. **通知模块** (Notification Module)
   - 邮件通知
   - 短信通知
   - 站内消息

### 数据流
[描述数据在系统中的流转过程]

## 部署架构
[描述系统部署架构，包括负载均衡、数据库部署等]

## 安全考虑
- 认证授权
- 数据加密
- 安全防护
"""

    # 03_implement 阶段文档
    task_breakdown_template = """# 任务分解清单

## 项目概览
- 项目名称：{project_name}
- 开始日期：{date}
- 预计完成：[待填写]

## 按模块分解的任务

### Module 1: [模块名称]

#### Task 1: [任务名称]
- **描述**：[详细描述任务内容]
- **负责人**：[待分配]
- **优先级**：高/中/低
- **估算**：[小时数/人天]
- **依赖**：[依赖的其他任务]
- **验收标准**：
  - [ ] [标准 1]
  - [ ] [标准 2]
- **状态**：待开始/进行中/已完成

#### Task 2: [任务名称]
- **描述**：[详细描述任务内容]
- **负责人**：[待分配]
- **优先级**：高/中/低
- **估算**：[小时数/人天]
- **依赖**：[依赖的其他任务]
- **验收标准**：
  - [ ] [标准 1]
  - [ ] [标准 2]
- **状态**：待开始/进行中/已完成

### Module 2: [模块名称]
[继续添加...]

## 里程碑
- **里程碑 1**：[日期] - [描述]
- **里程碑 2**：[日期] - [描述]
- **里程碑 3**：[日期] - [描述]

## 风险识别
- [风险 1]：[描述和应对措施]
- [风险 2]：[描述和应对措施]
"""

    # 创建文档文件
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    project_name = target_dir.name

    docs = [
        ("docs/01_specify/prd.md", prd_template),
        ("docs/01_specify/user_stories.md", user_stories_template),
        ("docs/01_specify/api_spec.md", api_spec_template),
        ("docs/02_plan/architecture.md", architecture_template),
        ("docs/03_implement/task_breakdown.md", task_breakdown_template),
    ]

    for doc_path, template in docs:
        full_path = target_dir / doc_path
        if not full_path.exists():
            # 先替换项目相关的变量，然后再处理模板中的 { } 冲突
            content = template.replace("{project_name}", project_name).replace("{date}", date_str)
            full_path.write_text(content, encoding='utf-8')
            print(f"  ✓ 创建文档模板: {doc_path}")


def copy_template(template_dir: Path, target_dir: Path, project_name: str):
    """复制模板并替换变量"""
    if target_dir.exists():
        print(f"错误: 项目已存在: {target_dir}")
        sys.exit(1)

    print(f"📦 从模板创建项目: {project_name}")
    print(f"📁 模板: {template_dir}")
    print(f"📁 目标: {target_dir}")
    print()

    # 创建项目目录结构
    target_dir.mkdir(exist_ok=True)

    # 复制模板内容（除了 .context，每个项目需要独立的）
    for item in template_dir.iterdir():
        if item.name == '.context':
            continue  # 跳过 .context，每个项目需要独立的
        if item.is_dir():
            shutil.copytree(item, target_dir / item.name,
                           ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            shutil.copy2(item, target_dir / item.name)

    # 创建项目特有的目录
    (target_dir / "src").mkdir(exist_ok=True)
    (target_dir / "tests").mkdir(exist_ok=True)
    (target_dir / "docs").mkdir(exist_ok=True)

    # 创建按 Phase 组织的文档结构
    docs_structure = [
        "01_specify",
        "02_plan",
        "03_implement",
        "04_test",
        "05_release"
    ]

    for phase_dir in docs_structure:
        (target_dir / "docs" / phase_dir).mkdir(exist_ok=True)

    # 创建 artifacts 目录
    (target_dir / "docs" / "artifacts").mkdir(exist_ok=True)
    (target_dir / "docs" / "artifacts" / "diagrams").mkdir(exist_ok=True)
    (target_dir / "docs" / "artifacts" / "mockups").mkdir(exist_ok=True)
    (target_dir / "docs" / "artifacts" / "meeting_notes").mkdir(exist_ok=True)

    # 创建项目独立的 .context 目录
    context_dir = target_dir / ".context"
    context_dir.mkdir(exist_ok=True)
    (context_dir / "modules").mkdir(exist_ok=True)

    # 创建项目独立的 .checkpoints 目录
    checkpoints_dir = target_dir / ".checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)

    # 创建基础文档模板
    create_doc_templates(target_dir)

    # 更新 .project_state.json
    state_file = target_dir / ".project_state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text())
        state["project_name"] = project_name
        state["created_at"] = datetime.now().isoformat()
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        # 如果模板中没有，创建一个
        state = {
            "project_name": project_name,
            "version": "0.1.0",
            "current_phase": "specify",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    # 更新 README.md 中的项目名
    readme_file = target_dir / "README.md"
    if readme_file.exists():
        content = readme_file.read_text()
        # 替换 template 为实际项目名
        content = content.replace("template", project_name)
        content = content.replace("Template", project_name.capitalize())
        readme_file.write_text(content)

    print(f"  ✓ 项目结构创建完成")


def init_git_repo(project_dir: Path, project_name: str):
    """初始化 Git 仓库"""
    print()
    print("🌳 初始化 Git 仓库...")

    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True
        )

        subprocess.run(
            ["git", "add", "."],
            cwd=project_dir,
            check=True,
            capture_output=True
        )

        commit_msg = f"""chore: initialize project {project_name}

Created from project-team-system template

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"""

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=project_dir,
            check=True,
            capture_output=True
        )

        print("  ✓ Git 仓库初始化完成")

    except Exception as e:
        print(f"  ⚠️  Git 初始化失败: {e}")


def print_summary(project_dir: Path, project_name: str):
    """打印总结"""
    project_team_root = get_project_team_root()

    print()
    print("=" * 60)
    print(f"✅ 项目 {project_name} 创建完成！")
    print("=" * 60)
    print()
    print(f"📁 位置: {project_dir}")
    print()
    print("📂 项目结构:")
    print("  ├── .project_state.json  # 项目状态")
    print("  ├── .context/            # 项目上下文索引")
    print("  ├── .checkpoints/        # 项目状态快照")
    print("  ├── src/                 # 源代码")
    print("  ├── tests/               # 测试代码")
    print("  ├── docs/                # 项目文档（按 5 Phase 组织）")
    print("  │   ├── 01_specify/      # 需求阶段")
    print("  │   │   ├── prd.md       # 产品需求文档")
    print("  │   │   ├── user_stories.md # 用户故事")
    print("  │   │   └── api_spec.md  # API 规范")
    print("  │   ├── 02_plan/         # 设计阶段")
    print("  │   │   └── architecture.md # 技术架构")
    print("  │   ├── 03_implement/    # 开发阶段")
    print("  │   │   └── task_breakdown.md # 任务清单")
    print("  │   ├── 04_test/         # 测试阶段")
    print("  │   └── 05_release/      # 发布阶段")
    print("  │   └── artifacts/       # 产出物")
    print("  │       ├── diagrams/    # 图表")
    print("  │       └── mockups/     # 原型")
    print("  ├── sop.yaml             # 开发流程")
    print("  ├── requirements.md      # 需求文档")
    print("  └── README.md")
    print()
    print("🔧 Project Agent 框架:")
    print(f"  └── {project_team_root.relative_to(project_dir.parent)}/")
    print("      ├── skills/           # 8 个开发技能")
    print("      ├── agents/           # Project Agent 定义")
    print("      └── CLAUDE.md         # 框架启动指南")
    print()
    print("🚀 下一步:")
    print(f"  cd {project_dir}")
    print(f"  vim requirements.md      # 1. 编写需求")
    print(f"  vim docs/01_specify/prd.md # 2. 编写 PRD")
    print(f"  # 3. 使用 Project Agent 开始开发")
    print(f"  #    (框架在 ../project_team/ 中)")
    print()
    print("📚 文档模板已创建:")
    print("  ✓ docs/01_specify/prd.md - 产品需求文档")
    print("  ✓ docs/01_specify/user_stories.md - 用户故事")
    print("  ✓ docs/01_specify/api_spec.md - API 规范")
    print("  ✓ docs/02_plan/architecture.md - 技术架构")
    print("  ✓ docs/03_implement/task_breakdown.md - 任务清单")
    print()
    print("💡 使用 Project Agent:")
    print("  # Claude 会自动读取 ../project_team/CLAUDE.md")
    print("  # 以 Project Agent 身份开始 5 Phase 开发流程")
    print("  # 每个阶段在对应的 docs/ 目录下记录产出")
    print()


def create_project_structure(project_name: str, target_dir: str = "."):
    """创建项目结构（主函数）"""

    # 获取模板目录
    template_dir = get_template_dir()

    # 目标项目目录
    project_dir = Path(target_dir).resolve() / project_name

    # 复制模板
    copy_template(template_dir, project_dir, project_name)

    # 初始化 Git
    init_git_repo(project_dir, project_name)

    # 打印总结
    print_summary(project_dir, project_name)


def main():
    if len(sys.argv) < 2:
        print("VibeKit - init_new_project.py")
        print()
        print("用法: python init_new_project.py <project_name> [target_dir]")
        print()
        print("示例:")
        print("  python project_team/skills/init_new_project.py my-todo-app")
        print("  python project_team/skills/init_new_project.py my-app ~/Projects")
        print()
        print("说明:")
        print("  - 在 project_team/ 同级目录创建新项目")
        print("  - 基于标准项目模板，包含 src/, tests/, docs/ 等")
        print("  - 自动初始化 Git 仓库")
        sys.exit(1)

    project_name = sys.argv[1]
    target_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    create_project_structure(project_name, target_dir)


if __name__ == "__main__":
    main()
