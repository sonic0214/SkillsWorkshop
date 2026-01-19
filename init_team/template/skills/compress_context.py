#!/usr/bin/env python3
"""
compress_context.py - 上下文压缩

功能:
- 读取任务相关的上下文指针
- 提取最小必要上下文
- 生成压缩的上下文摘要

设计原则 (insight_012):
- 指针式传递：只传指针，不传全量
- 按需检索：接收方可以进一步检索
- 避免上下文爆炸

使用:
    python compress_context.py <project_root> <task_id>
"""

import json
import sys
from pathlib import Path


def load_task(project_root: str, task_id: str) -> dict:
    """加载任务信息"""
    root = Path(project_root).resolve()
    tasks_file = root / "tasks.md"

    # 简化版：从 tasks.md 中解析任务
    # 实际项目中应该有更完善的任务管理格式
    if not tasks_file.exists():
        return {
            "id": task_id,
            "context_pointers": {}
        }

    # 这里可以实现更复杂的任务解析逻辑
    # MVP 阶段返回基础结构
    return {
        "id": task_id,
        "context_pointers": {
            "requirements": "requirements.md",
            "architecture": "architecture.md"
        }
    }


def extract_minimal_context(project_root: str, pointers: dict) -> dict:
    """提取最小上下文"""
    root = Path(project_root).resolve()
    context = {}

    for key, pointer in pointers.items():
        # 解析指针格式: file_path#section 或 file_path#line-N
        if '#' in pointer:
            file_path, anchor = pointer.split('#', 1)
        else:
            file_path, anchor = pointer, None

        full_path = root / file_path

        if not full_path.exists():
            context[key] = {"error": f"文件不存在: {file_path}"}
            continue

        # 读取文件内容（只提取预览）
        try:
            content = full_path.read_text()
            preview = content[:500] + "..." if len(content) > 500 else content

            context[key] = {
                "file": file_path,
                "anchor": anchor,
                "preview": preview,
                "full_size": len(content)
            }
        except Exception as e:
            context[key] = {"error": str(e)}

    return context


def compress_context(project_root: str, task_id: str) -> dict:
    """压缩上下文"""
    task = load_task(project_root, task_id)
    pointers = task.get("context_pointers", {})
    context = extract_minimal_context(project_root, pointers)

    result = {
        "task_id": task_id,
        "context_pointers": pointers,
        "minimal_context": context,
        "search_interface": {
            "description": "使用 search_in_module.py 进行按需检索",
            "examples": [
                f"python search_in_module.py {project_root} <module> list_files:api",
                f"python search_in_module.py {project_root} <module> find_symbol:<name>"
            ]
        },
        "metadata": {
            "compressed_by": "compress_context.py",
            "pointer_count": len(pointers),
            "context_count": len(context)
        }
    }

    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python compress_context.py <project_root> <task_id>")
        sys.exit(1)

    project_root = sys.argv[1]
    task_id = sys.argv[2]

    print(f"🔧 压缩任务上下文: {task_id}")
    result = compress_context(project_root, task_id)

    # 保存压缩上下文
    root = Path(project_root).resolve()
    output_dir = root / ".context"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"compressed_{task_id}.json"
    output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"✓ 压缩上下文已生成: {output_file}")
    print(f"  指针数: {result['metadata']['pointer_count']}")
    print(f"  上下文数: {result['metadata']['context_count']}")


if __name__ == "__main__":
    main()
