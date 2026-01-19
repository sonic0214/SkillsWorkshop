#!/usr/bin/env python3
"""recovery.py - 断点恢复工具

帮助新 Agent 从项目状态文件中恢复到正确的上下文。

Usage:
    python recovery.py <project_root> [--mode=ask|auto]

Example:
    python recovery.py ~/Project/my-app --mode=ask
    python recovery.py ~/Project/my-app --mode=auto
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def load_project_state(project_root: Path) -> Optional[Dict]:
    """加载项目状态文件"""
    state_file = project_root / ".project_state.json"
    if not state_file.exists():
        return None

    try:
        return json.loads(state_file.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ 无法读取项目状态文件: {e}")
        return None


def check_documentation_integrity(project_root: Path, current_phase: str) -> Dict:
    """检查文档完整性"""
    phase_docs = {
        "specify": ["docs/01_specify/prd.md", "docs/01_specify/user_stories.md"],
        "plan": ["docs/02_plan/architecture.md", "docs/02_plan/module_design.md"],
        "implement": ["docs/03_implement/task_breakdown.md", "docs/03_implement/progress_track.md"],
        "test": ["docs/04_test/test_plan.md", "docs/04_test/test_cases.md"],
        "release": ["docs/05_release/release_notes.md", "docs/05_release/deployment.md"]
    }

    # 检查当前 Phase 及之前的所有文档
    phase_order = ["specify", "plan", "implement", "test", "release"]
    current_index = phase_order.index(current_phase) if current_phase in phase_order else 0

    missing_docs = []
    existing_docs = []

    for phase in phase_order[:current_index + 1]:
        for doc in phase_docs.get(phase, []):
            doc_path = project_root / doc
            if doc_path.exists():
                existing_docs.append(doc)
            else:
                missing_docs.append(doc)

    return {
        "existing": existing_docs,
        "missing": missing_docs,
        "integrity_ok": len(missing_docs) == 0
    }


def check_git_status(project_root: Path) -> Dict:
    """检查 Git 状态"""
    try:
        import subprocess

        # 检查是否有未提交的变更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        has_uncommitted = len(result.stdout.strip()) > 0

        # 获取最新提交
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%an|%ar"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|")
            last_commit = {
                "hash": parts[0][:8],
                "message": parts[1],
                "author": parts[2],
                "time": parts[3]
            }
        else:
            last_commit = None

        # 获取提交总数
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        total_commits = int(result.stdout.strip()) if result.returncode == 0 else 0

        return {
            "available": True,
            "has_uncommitted": has_uncommitted,
            "last_commit": last_commit,
            "total_commits": total_commits,
            "clean": not has_uncommitted
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


def check_test_status(project_root: Path) -> Dict:
    """检查测试状态（如果有测试报告）"""
    quality_report = project_root / "docs/04_test/quality_report.md"
    if not quality_report.exists():
        return {
            "available": False,
            "message": "质量报告不存在"
        }

    try:
        content = quality_report.read_text(encoding='utf-8')

        # 提取测试通过率
        import re
        pass_rate_match = re.search(r'通过率[：:]\s*(\d+(?:\.\d+)?)%', content, re.IGNORECASE)
        pass_rate = float(pass_rate_match.group(1)) if pass_rate_match else None

        # 提取 Bug 数量
        p0_match = re.search(r'P0[：:]\s*(\d+)', content, re.IGNORECASE)
        p1_match = re.search(r'P1[：:]\s*(\d+)', content, re.IGNORECASE)

        p0_bugs = int(p0_match.group(1)) if p0_match else None
        p1_bugs = int(p1_match.group(1)) if p1_match else None

        return {
            "available": True,
            "pass_rate": pass_rate,
            "p0_bugs": p0_bugs,
            "p1_bugs": p1_bugs,
            "test_ok": (pass_rate or 0) >= 95 and (p0_bugs or 0) == 0
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


def load_latest_checkpoint(project_root: Path) -> Optional[Dict]:
    """加载最新的检查点"""
    checkpoints_dir = project_root / ".context/checkpoints"
    if not checkpoints_dir.exists():
        return None

    # 找到最新的检查点文件
    checkpoints = sorted(
        checkpoints_dir.glob("checkpoint_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if not checkpoints:
        return None

    try:
        latest = checkpoints[0]
        return {
            "file": latest.name,
            "data": json.loads(latest.read_text(encoding='utf-8')),
            "timestamp": datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
        }
    except Exception as e:
        print(f"⚠️  无法读取检查点文件: {e}")
        return None


def generate_recovery_report(project_root: Path, mode: str = "ask") -> Dict:
    """
    生成恢复报告

    Args:
        project_root: 项目根目录
        mode: 恢复模式 ("ask" 或 "auto")

    Returns:
        恢复报告字典
    """
    root = Path(project_root).resolve()

    # 1. 加载项目状态
    state = load_project_state(root)
    if not state:
        return {
            "status": "error",
            "message": "项目状态文件不存在，无法恢复。请检查 .project_state.json 文件。"
        }

    # 2. 提取关键信息
    current_phase = state.get("current_phase", "unknown")
    progress = state.get("progress", {})
    last_active = state.get("last_active_time", "未知")
    completed_tasks = state.get("completed_tasks", [])
    current_task = state.get("current_task", None)

    # 计算进度百分比
    total_tasks = progress.get("total_tasks", 0)
    completed_count = len(completed_tasks)
    progress_pct = (completed_count / total_tasks * 100) if total_tasks > 0 else 0

    # 3. 验证当前状态
    doc_check = check_documentation_integrity(root, current_phase)
    git_check = check_git_status(root)
    test_check = check_test_status(root)

    # 4. 加载最新检查点
    checkpoint = load_latest_checkpoint(root)

    # 5. 分析问题和警告
    warnings = []
    errors = []

    if not doc_check["integrity_ok"]:
        errors.append(f"文档不完整：缺少 {len(doc_check['missing'])} 个文档")
        for doc in doc_check["missing"]:
            errors.append(f"  - {doc}")

    if git_check.get("available") and git_check.get("has_uncommitted"):
        warnings.append("存在未提交的变更，建议先提交或保存")

    if test_check.get("available") and not test_check.get("test_ok"):
        warnings.append(f"测试状态异常：通过率 {test_check.get('pass_rate', 0)}%")

    # 6. 生成上下文指针
    context_pointers = {
        "architecture": f"docs/02_plan/architecture.md",
        "progress_track": f"docs/03_implement/progress_track.md",
        "last_commit": git_check.get("last_commit", {}).get("hash", "N/A"),
        "checkpoint": checkpoint.get("file") if checkpoint else None
    }

    # 7. 确定下一步任务
    if current_task:
        next_task = current_task
    elif completed_count < total_tasks:
        # 查找第一个未完成的任务（简化版，实际应从 task_breakdown.md 读取）
        next_task = {
            "id": f"#{completed_count + 1}",
            "description": "请查看 docs/03_implement/task_breakdown.md 确认"
        }
    else:
        next_task = None

    # 8. 决定恢复状态
    can_auto_recover = (
        doc_check["integrity_ok"] and
        git_check.get("clean", False) and
        (not test_check.get("available") or test_check.get("test_ok", True))
    )

    if mode == "auto" and not can_auto_recover:
        recovery_mode = "ask"  # 降级为询问模式
        warnings.append("自动恢复验证失败，已降级为询问模式")
    else:
        recovery_mode = mode

    # 9. 生成报告
    report = {
        "status": "ready" if can_auto_recover else "needs_attention",
        "recovery_mode": recovery_mode,
        "project_info": {
            "root": str(root),
            "last_active": last_active,
            "phase": current_phase,
            "progress_pct": round(progress_pct, 1)
        },
        "progress": {
            "total_tasks": total_tasks,
            "completed": completed_count,
            "remaining": total_tasks - completed_count,
            "last_completed_task": completed_tasks[-1] if completed_tasks else None,
            "next_task": next_task
        },
        "validation": {
            "documentation": doc_check,
            "git": git_check,
            "test": test_check
        },
        "context_pointers": context_pointers,
        "checkpoint": checkpoint,
        "warnings": warnings,
        "errors": errors,
        "can_auto_recover": can_auto_recover
    }

    return report


def print_recovery_report(report: Dict):
    """打印恢复报告"""
    print("\n" + "=" * 70)
    print("🔄 项目断点恢复报告")
    print("=" * 70)

    if report.get("status") == "error":
        print(f"\n❌ 错误: {report.get('message')}")
        print("=" * 70 + "\n")
        return

    info = report["project_info"]
    prog = report["progress"]

    # 项目基本信息
    print(f"\n📁 项目路径: {info['root']}")
    print(f"📅 上次活跃: {info['last_active']}")
    print(f"📍 当前 Phase: {info['phase']}")
    print(f"📊 进度: {prog['completed']}/{prog['total_tasks']} ({info['progress_pct']}%)")

    # 进度详情
    print(f"\n🎯 任务进度:")
    if prog['last_completed_task']:
        last_task = prog['last_completed_task']
        print(f"  ✅ 上次完成: {last_task.get('id', 'N/A')} - {last_task.get('description', 'N/A')}")
    else:
        print(f"  ⚠️  还没有完成任何任务")

    if prog['next_task']:
        next_task = prog['next_task']
        print(f"  🔜 下一个任务: {next_task.get('id', 'N/A')} - {next_task.get('description', 'N/A')}")
    else:
        print(f"  ✨ 所有任务已完成！")

    # 验证状态
    print(f"\n🔍 状态验证:")

    # 文档完整性
    doc_status = report["validation"]["documentation"]
    doc_icon = "✅" if doc_status["integrity_ok"] else "❌"
    print(f"  {doc_icon} 文档完整性: {len(doc_status['existing'])} 个文档存在")
    if not doc_status["integrity_ok"]:
        print(f"     缺少 {len(doc_status['missing'])} 个文档")

    # Git 状态
    git_status = report["validation"]["git"]
    if git_status.get("available"):
        git_icon = "✅" if git_status.get("clean") else "⚠️ "
        status_text = "干净" if git_status.get("clean") else "有未提交变更"
        print(f"  {git_icon} Git 状态: {status_text}")
        if git_status.get("last_commit"):
            commit = git_status["last_commit"]
            print(f"     最新提交: {commit['hash']} - {commit['message']} ({commit['time']})")
    else:
        print(f"  ⚠️  Git 不可用")

    # 测试状态
    test_status = report["validation"]["test"]
    if test_status.get("available"):
        test_icon = "✅" if test_status.get("test_ok") else "⚠️ "
        print(f"  {test_icon} 测试状态: 通过率 {test_status.get('pass_rate', 0)}%")
        if test_status.get("p0_bugs") is not None:
            print(f"     P0 Bug: {test_status['p0_bugs']}, P1 Bug: {test_status.get('p1_bugs', 0)}")
    else:
        print(f"  ℹ️  测试状态: 不可用（可能还未到测试阶段）")

    # 检查点
    if report.get("checkpoint"):
        cp = report["checkpoint"]
        print(f"\n💾 最新检查点:")
        print(f"  文件: {cp['file']}")
        print(f"  时间: {cp['timestamp']}")

    # 上下文指针
    print(f"\n📌 关键文件指针:")
    for key, path in report["context_pointers"].items():
        if path and path != "N/A":
            print(f"  - {key}: {path}")

    # 警告
    if report["warnings"]:
        print(f"\n⚠️  警告 ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"  - {warning}")

    # 错误
    if report["errors"]:
        print(f"\n❌ 错误 ({len(report['errors'])}):")
        for error in report["errors"]:
            print(f"  - {error}")

    # 恢复建议
    print(f"\n💡 恢复建议:")
    if report["can_auto_recover"]:
        print(f"  ✅ 状态验证通过，可以自动恢复")
        print(f"  🚀 建议: 直接继续执行下一个任务")
    else:
        print(f"  ⚠️  状态异常，建议人工介入")
        print(f"  🔧 建议:")
        if not report["validation"]["documentation"]["integrity_ok"]:
            print(f"     1. 补全缺失的文档")
        if report["validation"]["git"].get("has_uncommitted"):
            print(f"     2. 提交或撤销未提交的变更")
        if not report["validation"]["test"].get("test_ok", True):
            print(f"     3. 修复失败的测试")

    print("\n" + "=" * 70)
    print(f"🔄 恢复模式: {report['recovery_mode']}")
    if report['recovery_mode'] == 'ask':
        print("📋 下一步: Supervisor 应询问用户如何恢复")
    else:
        print("🤖 下一步: 自动恢复到上次状态并继续执行")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recovery.py <project_root> [--mode=ask|auto]")
        print("\nModes:")
        print("  ask  - 询问用户如何恢复（默认）")
        print("  auto - 自动验证并恢复（如果验证失败，降级为 ask 模式）")
        print("\nExample:")
        print("  python recovery.py ~/Project/my-app --mode=ask")
        print("  python recovery.py ~/Project/my-app --mode=auto")
        sys.exit(1)

    project_root = sys.argv[1]
    mode = "ask"  # 默认模式

    # 解析模式参数
    for arg in sys.argv[2:]:
        if arg.startswith("--mode="):
            mode = arg.split("=")[1]
            if mode not in ["ask", "auto"]:
                print(f"❌ 无效的模式: {mode}，只支持 ask 或 auto")
                sys.exit(1)

    print(f"🔍 分析项目: {project_root}")
    print(f"🔄 恢复模式: {mode}")

    report = generate_recovery_report(project_root, mode)
    print_recovery_report(report)

    # 以退出码表示状态
    sys.exit(0 if report.get("can_auto_recover") else 1)
