#!/usr/bin/env python3
"""build_main_index.py - 构建主索引树"""

import os
import json
import sys
from pathlib import Path


def scan_modules(src_dir):
    """扫描模块"""
    modules = {}
    if not src_dir.exists():
        return modules

    for item in src_dir.iterdir():
        if item.is_dir() and not item.name.startswith(('_', '.')):
            modules[item.name] = {
                "path": str(item.relative_to(src_dir.parent)),
                "layers": [],
                "module_index": f".context/modules/{item.name}_index.json"
            }
    return modules


def build_main_index(project_root):
    """构建主索引"""
    root = Path(project_root).resolve()
    src_dir = root / "src"
    modules = scan_modules(src_dir)

    index = {
        "version": "1.0.0",
        "project_root": str(root),
        "modules": modules,
        "module_dependencies": {},
        "metadata": {"total_modules": len(modules)}
    }
    return index


def save_index(index, project_root):
    """保存索引"""
    root = Path(project_root).resolve()
    context_dir = root / ".context"
    context_dir.mkdir(exist_ok=True)

    index_file = context_dir / "main_index.json"
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f"✓ 主索引已生成: {index_file}")
    print(f"  模块数: {index['metadata']['total_modules']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_main_index.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    print(f"🔍 扫描项目: {project_root}")
    index = build_main_index(project_root)
    save_index(index, project_root)
