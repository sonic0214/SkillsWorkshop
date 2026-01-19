#!/usr/bin/env python3
"""
build_module_index.py - 构建模块索引树

功能:
- 扫描指定模块的内部结构
- 识别分层 (api/service/db)
- 为每个文件记录 exports/imports
- 生成 .context/modules/{module}_index.json

设计原则 (insight_011):
- 模块索引 = 树内导航 (记录模块细节)
- 给 Dev 看的 (文件级视图)
- O(n) 复杂度，n = 文件数量

使用:
    python build_module_index.py <project_root> <module_name>
"""

import os
import json
import sys
from pathlib import Path
import ast


def scan_layer(layer_dir: Path) -> dict:
    """扫描某一层的文件"""
    files = []

    if not layer_dir.exists():
        return {"path": str(layer_dir), "files": []}

    for file in layer_dir.glob("*.py"):
        if file.name.startswith('_'):
            continue

        file_info = {
            "name": file.name,
            "path": str(file.relative_to(layer_dir.parent.parent)),
            "exports": extract_exports(file),
            "imports_from": extract_imports(file)
        }
        files.append(file_info)

    return {
        "path": str(layer_dir.relative_to(layer_dir.parent.parent)),
        "files": files
    }


def extract_exports(file_path: Path) -> list:
    """提取文件导出的符号 (函数/类)"""
    try:
        tree = ast.parse(file_path.read_text())
        exports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    exports.append(node.name)
            elif isinstance(node, ast.ClassDef):
                exports.append(node.name)

        return exports
    except:
        return []


def extract_imports(file_path: Path) -> list:
    """提取文件的导入依赖"""
    try:
        tree = ast.parse(file_path.read_text())
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return list(set(imports))
    except:
        return []


def build_module_index(project_root: str, module_name: str) -> dict:
    """构建模块索引"""
    root = Path(project_root).resolve()
    module_dir = root / "src" / module_name

    if not module_dir.exists():
        raise FileNotFoundError(f"模块不存在: {module_dir}")

    # 扫描各层
    structure = {}
    layers = ["api", "service", "db", "model", "controller", "repository"]

    for layer in layers:
        layer_dir = module_dir / layer
        if layer_dir.exists():
            structure[layer] = scan_layer(layer_dir)

    index = {
        "version": "1.0.0",
        "module_name": module_name,
        "module_path": str(module_dir.relative_to(root)),
        "structure": structure,
        "layer_flow": {
            "typical_flow": "api → service → db"
        },
        "metadata": {
            "total_layers": len(structure),
            "indexed_by": "build_module_index.py"
        }
    }

    return index


def save_index(index: dict, project_root: str, module_name: str):
    """保存索引到文件"""
    root = Path(project_root).resolve()
    modules_dir = root / ".context" / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)

    index_file = modules_dir / f"{module_name}_index.json"
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    print(f"✓ 模块索引已生成: {index_file}")
    print(f"  分层数: {index['metadata']['total_layers']}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python build_module_index.py <project_root> <module_name>")
        sys.exit(1)

    project_root = sys.argv[1]
    module_name = sys.argv[2]

    print(f"🔍 扫描模块: {module_name}")
    index = build_module_index(project_root, module_name)
    save_index(index, project_root, module_name)


if __name__ == "__main__":
    main()
