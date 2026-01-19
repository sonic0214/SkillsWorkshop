#!/usr/bin/env python3
"""validate_phase_gate.py - 阶段门禁检查器

验证 Phase 切换的前置条件，确保文档完整性和流程遵守。

Usage:
    python validate_phase_gate.py <project_root> <from_phase> <to_phase>

Example:
    python validate_phase_gate.py ~/Project/my-app specify plan
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Phase 要求配置
PHASE_REQUIREMENTS = {
    "specify": {
        "required_docs": [
            "docs/01_specify/prd.md",
            "docs/01_specify/user_stories.md"
        ],
        "optional_docs": [
            "docs/01_specify/api_spec.md"
        ],
        "min_total_words": 1000,
        "custom_checks": {
            "user_stories_count": 10  # 至少 10 个用户故事
        }
    },
    "plan": {
        "required_docs": [
            "docs/02_plan/architecture.md",
            "docs/02_plan/module_design.md"
        ],
        "required_files": [
            ".context/main_index.json"
        ],
        "min_total_words": 1500,
        "custom_checks": {
            "has_architecture_diagram": True  # 架构图存在
        }
    },
    "implement": {
        "required_docs": [
            "docs/03_implement/task_breakdown.md",
            "docs/03_implement/progress_track.md"
        ],
        "min_total_words": 500,
        "custom_checks": {
            "min_tasks": 20,  # 至少 20 个开发任务
            "git_commits": 1  # 至少有初始提交
        }
    },
    "test": {
        "required_docs": [
            "docs/04_test/test_plan.md",
            "docs/04_test/test_cases.md",
            "docs/04_test/quality_report.md"
        ],
        "min_total_words": 2000,
        "custom_checks": {
            "min_test_cases": 100,  # 至少 100 个测试用例
            "min_pass_rate": 95  # 测试通过率 >= 95%
        }
    },
    "release": {
        "required_docs": [
            "docs/05_release/release_notes.md",
            "docs/05_release/deployment.md"
        ],
        "min_total_words": 800,
        "custom_checks": {
            "p0_bugs": 0,  # P0 Bug = 0
            "p1_bugs": 0   # P1 Bug = 0
        }
    }
}


def count_words_in_file(file_path: Path) -> int:
    """统计文件字数（中文字符 + 英文单词）"""
    try:
        content = file_path.read_text(encoding='utf-8')
        # 简单统计：中文字符 + 空格分隔的单词
        chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        english_words = len([w for w in content.split() if w.strip()])
        return chinese_chars + english_words
    except Exception as e:
        print(f"⚠️  无法读取文件 {file_path}: {e}")
        return 0


def check_file_exists(project_root: Path, rel_path: str) -> Tuple[bool, str]:
    """检查文件是否存在"""
    file_path = project_root / rel_path
    exists = file_path.exists() and file_path.is_file()
    return exists, str(file_path)


def check_user_stories_count(project_root: Path) -> int:
    """检查用户故事数量（统计 "## US-" 或 "### US-" 的出现次数）"""
    user_stories_file = project_root / "docs/01_specify/user_stories.md"
    if not user_stories_file.exists():
        return 0

    content = user_stories_file.read_text(encoding='utf-8')
    count = content.count("## US-") + content.count("### US-")
    return count


def check_architecture_diagram(project_root: Path) -> bool:
    """检查架构图是否存在（简单检测 mermaid 代码块或图片链接）"""
    arch_file = project_root / "docs/02_plan/architecture.md"
    if not arch_file.exists():
        return False

    content = arch_file.read_text(encoding='utf-8')
    has_mermaid = "```mermaid" in content
    has_image = ("![" in content and "](" in content) or ("<img" in content)
    return has_mermaid or has_image


def check_task_count(project_root: Path) -> int:
    """检查任务数量（统计 "- [ ]" 或 "- [x]" 的出现次数）"""
    task_file = project_root / "docs/03_implement/task_breakdown.md"
    if not task_file.exists():
        return 0

    content = task_file.read_text(encoding='utf-8')
    count = content.count("- [ ]") + content.count("- [x]")
    return count


def check_git_commits(project_root: Path) -> int:
    """检查 Git 提交数量"""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
        return 0
    except Exception:
        return 0


def check_test_cases_count(project_root: Path) -> int:
    """检查测试用例数量"""
    test_cases_file = project_root / "docs/04_test/test_cases.md"
    if not test_cases_file.exists():
        return 0

    content = test_cases_file.read_text(encoding='utf-8')
    # 统计 "### TC-" 或 "## TC-"
    count = content.count("### TC-") + content.count("## TC-")
    return count


def extract_test_pass_rate(project_root: Path) -> float:
    """从质量报告中提取测试通过率"""
    quality_report = project_root / "docs/04_test/quality_report.md"
    if not quality_report.exists():
        return 0.0

    content = quality_report.read_text(encoding='utf-8')
    # 查找类似 "通过率: 95%" 或 "Pass Rate: 95%"
    import re
    patterns = [
        r'通过率[：:]\s*(\d+(?:\.\d+)?)%',
        r'Pass Rate[：:]\s*(\d+(?:\.\d+)?)%'
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0.0


def extract_bug_count(project_root: Path, severity: str) -> int:
    """从质量报告中提取 Bug 数量"""
    quality_report = project_root / "docs/04_test/quality_report.md"
    if not quality_report.exists():
        return 0

    content = quality_report.read_text(encoding='utf-8')
    # 查找类似 "P0: 0" 或 "P0 Bug: 0"
    import re
    patterns = [
        rf'{severity}[：:]\s*(\d+)',
        rf'{severity}\s+Bug[s]?[：:]\s*(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


def run_custom_checks(project_root: Path, phase: str, checks: Dict) -> List[Tuple[str, bool, str]]:
    """运行自定义检查"""
    results = []

    if phase == "specify":
        if "user_stories_count" in checks:
            required = checks["user_stories_count"]
            actual = check_user_stories_count(project_root)
            passed = actual >= required
            msg = f"用户故事数量: {actual} (要求 >= {required})"
            results.append(("用户故事数量", passed, msg))

    elif phase == "plan":
        if "has_architecture_diagram" in checks:
            passed = check_architecture_diagram(project_root)
            msg = "架构图存在" if passed else "架构图缺失（需要 mermaid 代码块或图片链接）"
            results.append(("架构图", passed, msg))

    elif phase == "implement":
        if "min_tasks" in checks:
            required = checks["min_tasks"]
            actual = check_task_count(project_root)
            passed = actual >= required
            msg = f"开发任务数量: {actual} (要求 >= {required})"
            results.append(("开发任务数量", passed, msg))

        if "git_commits" in checks:
            required = checks["git_commits"]
            actual = check_git_commits(project_root)
            passed = actual >= required
            msg = f"Git 提交数: {actual} (要求 >= {required})"
            results.append(("Git 提交", passed, msg))

    elif phase == "test":
        if "min_test_cases" in checks:
            required = checks["min_test_cases"]
            actual = check_test_cases_count(project_root)
            passed = actual >= required
            msg = f"测试用例数量: {actual} (要求 >= {required})"
            results.append(("测试用例数量", passed, msg))

        if "min_pass_rate" in checks:
            required = checks["min_pass_rate"]
            actual = extract_test_pass_rate(project_root)
            passed = actual >= required
            msg = f"测试通过率: {actual}% (要求 >= {required}%)"
            results.append(("测试通过率", passed, msg))

    elif phase == "release":
        if "p0_bugs" in checks:
            required = checks["p0_bugs"]
            actual = extract_bug_count(project_root, "P0")
            passed = actual <= required
            msg = f"P0 Bug 数量: {actual} (要求 <= {required})"
            results.append(("P0 Bug", passed, msg))

        if "p1_bugs" in checks:
            required = checks["p1_bugs"]
            actual = extract_bug_count(project_root, "P1")
            passed = actual <= required
            msg = f"P1 Bug 数量: {actual} (要求 <= {required})"
            results.append(("P1 Bug", passed, msg))

    return results


def validate_phase_gate(project_root: str, from_phase: str, to_phase: str) -> Dict:
    """
    验证 Phase 切换的前置条件

    Args:
        project_root: 项目根目录
        from_phase: 当前 Phase
        to_phase: 目标 Phase

    Returns:
        验证结果字典
    """
    root = Path(project_root).resolve()

    # 验证 from_phase 的完成条件
    if from_phase not in PHASE_REQUIREMENTS:
        return {
            "passed": False,
            "from_phase": from_phase,
            "to_phase": to_phase,
            "error": f"未知的 Phase: {from_phase}"
        }

    requirements = PHASE_REQUIREMENTS[from_phase]
    results = {
        "passed": True,
        "from_phase": from_phase,
        "to_phase": to_phase,
        "checks": {
            "required_docs": [],
            "optional_docs": [],
            "required_files": [],
            "word_count": {},
            "custom_checks": []
        },
        "warnings": [],
        "errors": []
    }

    # 1. 检查必需文档
    for doc in requirements.get("required_docs", []):
        exists, full_path = check_file_exists(root, doc)
        results["checks"]["required_docs"].append({
            "path": doc,
            "exists": exists,
            "full_path": full_path
        })
        if not exists:
            results["passed"] = False
            results["errors"].append(f"缺少必需文档: {doc}")

    # 2. 检查可选文档（仅警告）
    for doc in requirements.get("optional_docs", []):
        exists, full_path = check_file_exists(root, doc)
        results["checks"]["optional_docs"].append({
            "path": doc,
            "exists": exists,
            "full_path": full_path
        })
        if not exists:
            results["warnings"].append(f"建议添加文档: {doc}")

    # 3. 检查必需文件（如索引文件）
    for file in requirements.get("required_files", []):
        exists, full_path = check_file_exists(root, file)
        results["checks"]["required_files"].append({
            "path": file,
            "exists": exists,
            "full_path": full_path
        })
        if not exists:
            results["passed"] = False
            results["errors"].append(f"缺少必需文件: {file}")

    # 4. 检查文档字数
    total_words = 0
    for doc_info in results["checks"]["required_docs"]:
        if doc_info["exists"]:
            word_count = count_words_in_file(Path(doc_info["full_path"]))
            results["checks"]["word_count"][doc_info["path"]] = word_count
            total_words += word_count

    min_words = requirements.get("min_total_words", 0)
    results["checks"]["word_count"]["total"] = total_words
    results["checks"]["word_count"]["required"] = min_words

    if total_words < min_words:
        results["passed"] = False
        results["errors"].append(
            f"文档字数不足: {total_words} (要求 >= {min_words})"
        )

    # 5. 运行自定义检查
    custom_checks = requirements.get("custom_checks", {})
    if custom_checks:
        check_results = run_custom_checks(root, from_phase, custom_checks)
        for check_name, passed, message in check_results:
            results["checks"]["custom_checks"].append({
                "name": check_name,
                "passed": passed,
                "message": message
            })
            if not passed:
                results["passed"] = False
                results["errors"].append(message)

    return results


def print_validation_report(results: Dict):
    """打印验证报告"""
    print("\n" + "=" * 60)
    print(f"📋 Phase Gate 验证报告")
    print("=" * 60)
    print(f"从 Phase: {results['from_phase']}")
    print(f"到 Phase: {results['to_phase']}")
    print(f"验证结果: {'✅ 通过' if results['passed'] else '❌ 失败'}")
    print("=" * 60)

    # 必需文档
    print("\n1️⃣  必需文档检查:")
    for doc in results["checks"]["required_docs"]:
        status = "✅" if doc["exists"] else "❌"
        print(f"  {status} {doc['path']}")

    # 可选文档
    if results["checks"]["optional_docs"]:
        print("\n2️⃣  可选文档检查:")
        for doc in results["checks"]["optional_docs"]:
            status = "✅" if doc["exists"] else "⚠️ "
            print(f"  {status} {doc['path']}")

    # 必需文件
    if results["checks"]["required_files"]:
        print("\n3️⃣  必需文件检查:")
        for file in results["checks"]["required_files"]:
            status = "✅" if file["exists"] else "❌"
            print(f"  {status} {file['path']}")

    # 文档字数
    word_count = results["checks"]["word_count"]
    print(f"\n4️⃣  文档字数检查:")
    print(f"  总字数: {word_count['total']} (要求 >= {word_count['required']})")
    status = "✅" if word_count['total'] >= word_count['required'] else "❌"
    print(f"  {status} {'通过' if status == '✅' else '不通过'}")

    # 自定义检查
    if results["checks"]["custom_checks"]:
        print(f"\n5️⃣  自定义检查:")
        for check in results["checks"]["custom_checks"]:
            status = "✅" if check["passed"] else "❌"
            print(f"  {status} {check['message']}")

    # 警告
    if results["warnings"]:
        print(f"\n⚠️  警告 ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"  - {warning}")

    # 错误
    if results["errors"]:
        print(f"\n❌ 错误 ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"  - {error}")

    print("\n" + "=" * 60)

    if results["passed"]:
        print("✅ 验证通过！可以切换到下一个 Phase。")
    else:
        print("❌ 验证失败！请修复上述错误后重试。")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python validate_phase_gate.py <project_root> <from_phase> <to_phase>")
        print("\nPhases: specify, plan, implement, test, release")
        print("\nExample:")
        print("  python validate_phase_gate.py ~/Project/my-app specify plan")
        sys.exit(1)

    project_root = sys.argv[1]
    from_phase = sys.argv[2]
    to_phase = sys.argv[3]

    print(f"🔍 验证项目: {project_root}")
    print(f"📍 Phase 切换: {from_phase} → {to_phase}")

    results = validate_phase_gate(project_root, from_phase, to_phase)
    print_validation_report(results)

    # 以退出码表示验证结果
    sys.exit(0 if results["passed"] else 1)
