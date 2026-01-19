#!/usr/bin/env python3
"""
init_team - 初始化团队协作系统实例

功能:
- 从 skill 内部模板复制 project-team-system 到目标位置
- 保持完整的 8 个 Skill 脚本、文档、模板
- 支持创建新实例或分发系统
- 支持附带需求初稿（从 MyBrain handoff/ 交接）
- v6.0 新增：支持三级 SOP 模式选择（Fast Track/Standard/Rigorous）

使用:
    # 创建空白项目（默认 Standard 模式）
    python skills/init_team/create.py --target ~/new-location

    # 创建带需求初稿的项目（自动评估复杂度，推荐 SOP 模式）
    python skills/init_team/create.py \
        --target ~/new-location \
        --requirements handoff/project_requirements.md

    # 手动指定 SOP 模式
    python skills/init_team/create.py \
        --target ~/new-location \
        --mode fast_track  # 或 standard / rigorous

模板位置:
    skills/init_team/template/
    - 模板随 skill 一起维护
    - skill 自包含，便于移植

设计原则:
- 自包含：skill 的所有依赖都在内部
- 单一数据源：templates/project-team-system 是唯一模板
- 封装性：skill 目录可独立复制和分发
- Adam → Project Agent 交接：需求初稿随项目携带
- v6.0: 复杂度自适应 SOP 模式

设计依据:
- session_004 v3.0
- session_008: Adam-Project Agent 协作流程
- session_011: v6.0 三级 SOP 模式
- insight_013: Agent vs Skill 边界
"""

import shutil
import sys
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime


def get_source_dir() -> Path:
    """获取源团队协作系统模板目录"""
    # 模板在当前 skill 目录下
    skill_dir = Path(__file__).parent
    source_dir = skill_dir / "template"

    if not source_dir.exists():
        raise FileNotFoundError(
            f"模板目录不存在: {source_dir}\n"
            f"这不应该发生，请检查 skill 安装是否完整"
        )

    return source_dir


def assess_project_complexity(requirements_file: Path) -> tuple[str, float]:
    """
    评估项目复杂度并推荐 SOP 模式

    Returns:
        (推荐模式, 复杂度得分)
    """
    skill_dir = Path(__file__).parent
    assess_script = skill_dir / "template" / "skills" / "assess_complexity.py"

    if not assess_script.exists():
        print("⚠️  复杂度评估脚本不存在，使用默认 standard 模式")
        return "standard", 0.5

    try:
        result = subprocess.run(
            [sys.executable, str(assess_script),
             "--requirements", str(requirements_file),
             "--non-interactive"],
            capture_output=True,
            text=True
        )

        # 解析输出找到推荐模式
        output = result.stdout

        # 从输出中提取推荐的 SOP 文件
        for line in output.split('\n'):
            if '建议使用 SOP:' in line:
                # 例如: "💡 建议使用 SOP: sop_fast_track.yaml"
                sop_file = line.split(':')[-1].strip()
                if 'fast_track' in sop_file:
                    mode = 'fast_track'
                elif 'rigorous' in sop_file:
                    mode = 'rigorous'
                else:
                    mode = 'standard'

                # 尝试提取得分
                score = 0.5
                for score_line in output.split('\n'):
                    if '综合复杂度得分:' in score_line:
                        try:
                            score_str = score_line.split(':')[-1].strip().split('/')[0].strip()
                            score = float(score_str)
                        except:
                            pass

                return mode, score

        # 如果没有找到推荐，使用默认
        return "standard", 0.5

    except Exception as e:
        print(f"⚠️  复杂度评估失败: {e}")
        print("使用默认 standard 模式")
        return "standard", 0.5


def select_sop_mode(mode: str = None, requirements_file: Path = None) -> tuple[str, float]:
    """
    选择 SOP 模式

    Args:
        mode: 用户手动指定的模式（可选）
        requirements_file: 需求文件（用于自动评估）

    Returns:
        (选择的模式, 复杂度得分)
    """
    valid_modes = ['fast_track', 'standard', 'rigorous']

    # 如果用户手动指定了模式
    if mode:
        if mode not in valid_modes:
            print(f"❌ 无效的模式: {mode}")
            print(f"有效模式: {', '.join(valid_modes)}")
            sys.exit(1)
        print(f"📋 使用用户指定的 SOP 模式: {mode}")
        return mode, 0.0  # 手动指定时得分为0

    # 如果有需求文件，自动评估
    if requirements_file and requirements_file.exists():
        print("📊 正在评估项目复杂度...")
        mode, score = assess_project_complexity(requirements_file)
        print(f"📊 复杂度得分: {score:.2f}")
        print(f"📋 推荐 SOP 模式: {mode}")

        # 询问用户是否接受推荐
        response = input(f"是否接受推荐的 {mode} 模式？(yes/no，直接回车默认 yes): ").strip().lower()
        if response and response != 'yes' and response != 'y':
            print("请手动选择模式:")
            print("  1. fast_track - 快速原型验证")
            print("  2. standard - 标准开发流程（推荐）")
            print("  3. rigorous - 严格质量控制")
            choice = input("选择 (1/2/3，直接回车默认 2): ").strip()

            if choice == '1':
                mode = 'fast_track'
            elif choice == '3':
                mode = 'rigorous'
            else:
                mode = 'standard'

            print(f"📋 使用用户选择的模式: {mode}")

        return mode, score

    # 空白项目，使用默认 standard 模式
    print("📋 使用默认 SOP 模式: standard")
    return "standard", 0.0


def update_project_state(target_dir: Path, requirements_file: Path = None,
                         sop_mode: str = "standard", complexity_score: float = 0.0):
    """更新项目状态文件，记录交接信息"""
    state_file = target_dir / ".project_state.json"

    # 更新交接信息
    state = {
        "system_version": "project-team-system v6.0",
        "created_by": "MyBrain/skills/init_team/create.py",
        "created_at": datetime.now().isoformat(),
        "sop_mode": sop_mode,
        "complexity_score": complexity_score
    }

    if requirements_file:
        state.update({
            "handoff_from": "MyBrain (Adam - Manager Agent)",
            "handoff_date": datetime.now().isoformat(),
            "initial_requirements": "requirements.md",
            "status": "initialized_with_requirements"
        })
    else:
        state.update({
            "status": "initialized"
        })

    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def create_root_readme(target_dir: Path):
    """创建项目根目录的 README.md"""
    readme_content = """# 项目开发环境

## 目录结构

```
.
├── project_team/           # project-team-system 开发框架（只读）
│   ├── skills/             # 开发技能脚本（含复杂度评估）
│   ├── agents/             # Project Agent 定义
│   ├── sop_templates/      # SOP 模板库
│   ├── examples/           # 学习示例
│   ├── docs/               # 框架文档
│   └── constraints/        # 约束文档
├── sop.yaml                # 项目 SOP 配置（从模板复制）
├── requirements.md         # 项目需求（如果存在）
├── .project_state.json     # 项目状态
├── CLAUDE.md               # Project Agent 启动指南
└── README.md               # 本文件
```

## 快速开始

### 1. 使用 Project Agent 开发新项目

```bash
# 进入项目环境
cd <your-project>

# 启动 Project Agent（会自动读取 project_team/CLAUDE.md）
# Claude 会以 Project Agent 身份启动，询问当前任务
```

### 2. 创建具体项目

```bash
# 使用框架创建具体项目
python project_team/skills/create_project_structure.py my-project

# 进入具体项目目录
cd my-project

# 开始开发（遵循 5 Phase 流程）
```

## 开发流程

1. **Specify (PM Mode)** - 分析需求，编写 User Stories
2. **Plan (Architect Mode)** - 设计架构，构建主索引
3. **Implement (Dev Mode)** - TDD 开发，模块化实现
4. **Test (QA Mode)** - 集成测试，质量保证
5. **Release (Architect Mode)** - 代码审查，发布准备

## 框架文档

详细文档请参考：
- `project_team/README.md` - 框架使用指南
- `project_team/docs/ARCHITECTURE.md` - 架构设计
- `project_team/docs/SKILLS.md` - 技能脚本参考

---

*由 project-team-system v3.0 驱动*
"""

    readme_file = target_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✓ 项目根 README.md 已创建")


def generate_claude_md(target_dir: Path, requirements_file: Path = None):
    """生成项目的 CLAUDE.md 文件"""
    template_file = Path(__file__).parent / "template" / "CLAUDE.md.template"
    target_file = target_dir / "CLAUDE.md"

    if not template_file.exists():
        print("⚠️  CLAUDE.md 模板不存在，跳过生成")
        return

    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 根据是否有需求文件调整内容
    if requirements_file:
        content = content.replace(
            "读取以下核心文件：\n\n1. **`agents/project_agent.md`** - 你的角色定义、4 种工作模式\n2. **`project_template/requirements.md`** - 项目需求（如果存在）",
            "读取以下核心文件：\n\n1. **`project_team/agents/project_agent.md`** - 你的角色定义、4 种工作模式\n2. **`requirements.md`** - 项目需求（已提供）"
        )
        content = content.replace(
            "2. **`project_template/requirements.md`** - 项目需求（如果存在）",
            "2. **`requirements.md`** - 项目需求（已提供）"
        )
        content = content.replace(
            "1. **`agents/project_agent.md`** - 你的角色定义、4 种工作模式",
            "1. **`project_team/agents/project_agent.md`** - 你的角色定义、4 种工作模式"
        )

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ CLAUDE.md 已生成（Project Agent 启动指南）")


def replicate_system(source_dir: Path, target_dir: Path, requirements_file: Path = None,
                    sop_mode: str = None):
    """复制整个系统，可选附带需求初稿"""
    print("=" * 60)
    print("🚀 创建 project-team-system 开发实例 (v6.0)")
    print("=" * 60)
    print()
    print(f"📁 源目录: {source_dir}")
    print(f"📁 目标目录: {target_dir}")
    if requirements_file:
        print(f"📄 需求初稿: {requirements_file}")
    print()

    # 选择 SOP 模式
    selected_mode, complexity_score = select_sop_mode(sop_mode, requirements_file)
    print()

    if target_dir.exists():
        response = input(f"⚠️  目标目录已存在，是否覆盖? (yes/no): ")
        if response.lower() != "yes":
            print("操作取消")
            sys.exit(0)
        shutil.rmtree(target_dir)

    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)

    # 创建 project_team 子目录
    project_team_dir = target_dir / "project_team"

    # 复制框架到 project_team 目录
    print("📦 复制 project-team-system 框架...")
    shutil.copytree(
        source_dir,
        project_team_dir,
        ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc', '.DS_Store',
            'examples/*/src', 'examples/*/tests'  # 排除示例项目的代码
        )
    )

    # v6.0: 选择和复制对应的 SOP 文件到项目根目录
    print(f"📋 配置 SOP 模式: {selected_mode}")
    sop_source = project_team_dir / "sop_templates" / f"sop_{selected_mode}.yaml"
    sop_target = target_dir / "sop.yaml"  # 复制到项目根目录

    if sop_source.exists():
        shutil.copy(sop_source, sop_target)
        print(f"✓ SOP 文件已配置: sop_{selected_mode}.yaml → sop.yaml")
    else:
        print(f"⚠️  SOP 源文件不存在: {sop_source}")
        print(f"   请检查 template/sop_templates/ 目录")

    # 复制 .gitignore 到项目根目录
    gitignore_source = source_dir / ".gitignore"
    if gitignore_source.exists():
        gitignore_target = target_dir / ".gitignore"
        shutil.copy(gitignore_source, gitignore_target)
        print(f"✓ .gitignore 已复制到项目根目录")

    # 生成项目的 CLAUDE.md 文件
    generate_claude_md(target_dir, requirements_file)

    # 如果提供了需求文件，复制到项目根目录
    if requirements_file and requirements_file.exists():
        target_req = target_dir / "requirements.md"
        shutil.copy(requirements_file, target_req)
        print(f"📄 需求初稿已复制: requirements.md")

        # 更新项目状态
        update_project_state(target_dir, requirements_file, selected_mode, complexity_score)
        print(f"✓ 项目状态已更新（记录交接信息和 SOP 模式）")
    else:
        # 空白项目
        update_project_state(target_dir, None, selected_mode, complexity_score)

    # 创建项目根目录的基础文件
    create_root_readme(target_dir)

    # 重新初始化 git
    print("🌳 初始化 Git 仓库...")
    try:
        subprocess.run(
            ["git", "init"],
            cwd=target_dir,
            check=True,
            capture_output=True
        )

        subprocess.run(
            ["git", "add", "."],
            cwd=target_dir,
            check=True,
            capture_output=True
        )

        commit_msg_parts = [
            "chore: initialize project-team-system",
            "",
            "Created by: MyBrain/skills/init_team/create.py",
            f"Source: {source_dir}",
            "Design: session_004 v3.0",
        ]

        if requirements_file:
            commit_msg_parts.append(f"Handoff from: MyBrain (Adam)")
            commit_msg_parts.append(f"Requirements: {requirements_file.name}")

        commit_msg_parts.extend([
            "",
            "🤖 Generated with Claude Code",
            "Co-Authored-By: Claude <noreply@anthropic.com>"
        ])

        commit_msg = "\n".join(commit_msg_parts)

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=target_dir,
            check=True,
            capture_output=True
        )

        print("  ✓ Git 仓库初始化完成")

    except Exception as e:
        print(f"  ⚠️  Git 初始化失败: {e}")

    print()
    print("=" * 60)
    print("✅ project-team-system 开发实例创建完成！")
    print("=" * 60)
    print()
    print(f"📁 位置: {target_dir}")
    print(f"📋 SOP 模式: {selected_mode.upper()}")
    if complexity_score > 0:
        print(f"📊 复杂度得分: {complexity_score:.2f}")
    print()
    print("📂 包含内容:")
    print("  ✓ project_team/ - 完整开发框架 (v6.0)")
    print("    ├─ skills/ (8+ 个技能脚本)")
    print("    ├─ agents/ (Project Agent 定义)")
    print("    ├─ examples/ (学习示例)")
    print("    └─ docs/ (框架文档)")
    print("  ✓ CLAUDE.md (Project Agent 启动指南)")
    print("  ✓ README.md (项目使用指南)")
    print(f"  ✓ SOP: {selected_mode} 模式")
    print("  ✓ .gitignore")
    if requirements_file:
        print("  ✓ requirements.md (需求初稿)")
    print()
    print("🚀 下一步:")
    print(f"  cd {target_dir}")
    print(f"  cat CLAUDE.md  # 查看 Project Agent 启动指南")
    if requirements_file:
        print(f"  cat requirements.md  # 查看需求初稿")
    else:
        print(f"  cat README.md")
    print()
    if not requirements_file:
        print("💡 创建具体项目:")
        print(f"  cd {target_dir}")
        print(f"  python project_team/skills/create_project_structure.py my-project")
        print()
    else:
        print("💡 Project Agent 启动时会自动读取需求初稿")
        print()
    print("🎯 项目代码与框架完全分离，可以开始开发！")
    print()


def verify_source(source_dir: Path):
    """验证源目录完整性"""
    required_items = [
        "skills/build_main_index.py",
        "skills/run_tdd_cycle.py",
        "skills/checkpoint.py",
        "skills/assess_complexity.py",
        "agents/project_agent.md",
        "sop_templates/sop_standard.yaml",
        "sop_templates/sop_fast_track.yaml",
        "sop_templates/sop_rigorous.yaml",
        "README.md"
    ]

    missing = []
    for item in required_items:
        if not (source_dir / item).exists():
            missing.append(item)

    if missing:
        print(f"⚠️  源目录不完整，缺少以下文件:")
        for item in missing:
            print(f"  - {item}")
        print()
        print("请确保 project-team-system 已正确创建")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="创建 project-team-system 实例（从源仓库复制）v6.0"
    )
    parser.add_argument(
        "--target",
        required=True,
        help="目标目录 (例如: ~/new-project-team-system)"
    )
    parser.add_argument(
        "--requirements",
        required=False,
        help="需求初稿文件路径 (例如: handoff/project_requirements.md)"
    )
    parser.add_argument(
        "--mode",
        required=False,
        choices=['fast_track', 'standard', 'rigorous'],
        help="SOP 模式 (fast_track/standard/rigorous)，不指定则自动评估"
    )

    args = parser.parse_args()

    # 获取源目录
    source_dir = get_source_dir()

    # 验证源目录
    verify_source(source_dir)

    # 目标目录
    target_dir = Path(args.target).expanduser().resolve()

    # 需求文件（可选）
    requirements_file = None
    if args.requirements:
        requirements_file = Path(args.requirements).resolve()
        if not requirements_file.exists():
            print(f"❌ 需求文件不存在: {requirements_file}")
            sys.exit(1)

    # 复制系统（v6.0 新增 sop_mode 参数）
    replicate_system(source_dir, target_dir, requirements_file, args.mode)


if __name__ == "__main__":
    main()
