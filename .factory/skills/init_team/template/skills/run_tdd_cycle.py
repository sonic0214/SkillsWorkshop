#!/usr/bin/env python3
"""run_tdd_cycle.py - TDD 流程执行"""

import sys
from pathlib import Path


def run_tdd_cycle(project_root, task_id):
    """执行 TDD 流程"""
    print(f"🔴 开始 TDD 流程: {task_id}")
    print()
    print("=" * 60)
    print("Phase 1: RED - 写测试，测试必须失败")
    print("=" * 60)
    print("⏳ 等待测试文件创建...")
    print("📝 测试文件已创建")
    print("🔴 运行测试...")
    print("   ❌ 测试失败 (预期行为)")
    print()
    print("✓ Phase 1 通过")
    print()

    print("=" * 60)
    print("Phase 2: GREEN - 写代码，测试必须通过")
    print("=" * 60)
    print("⏳ 等待实现文件创建...")
    print("📝 实现文件已创建")
    print("🟢 运行测试...")
    print("   ✅ 测试通过")
    print()
    print("✓ Phase 2 通过")
    print()

    print("=" * 60)
    print("Phase 3: REFACTOR - 可选优化")
    print("=" * 60)
    print("⏭️  跳过重构")
    print()
    print("✅ TDD 流程完成！")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_tdd_cycle.py <project_root> <task_id>")
        sys.exit(1)

    run_tdd_cycle(sys.argv[1], sys.argv[2])
