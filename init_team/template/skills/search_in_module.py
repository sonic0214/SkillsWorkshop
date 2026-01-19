#!/usr/bin/env python3
"""
search_in_module.py - 模块内搜索

功能:
- 基于模块索引进行搜索
- 支持多种查询类型
- 按需返回文件内容或符号定义

查询类型:
- list_files:<layer>          # 列出某层的所有文件
- read_file:<layer>/<file>    # 读取指定文件
- find_symbol:<symbol_name>   # 查找符号定义

使用:
    python search_in_module.py <project_root> <module_name> <query>

示例:
    python search_in_module.py . auth list_files:api
    python search_in_module.py . auth read_file:api/login.py
    python search_in_module.py . auth find_symbol:authenticate
"""

import json
import sys
from pathlib import Path


def load_module_index(project_root: str, module_name: str) -> dict:
    """加载模块索引"""
    root = Path(project_root).resolve()
    index_file = root / ".context" / "modules" / f"{module_name}_index.json"

    if not index_file.exists():
        raise FileNotFoundError(f"模块索引不存在: {index_file}")

    return json.loads(index_file.read_text())


def query_list_files(index: dict, layer: str) -> dict:
    """查询: 列出某层的所有文件"""
    if layer not in index["structure"]:
        return {"error": f"层不存在: {layer}"}

    files = index["structure"][layer]["files"]
    return {
        "layer": layer,
        "files": [f["name"] for f in files],
        "count": len(files)
    }


def query_read_file(index: dict, project_root: str, file_path: str) -> dict:
    """查询: 读取指定文件"""
    root = Path(project_root).resolve()
    full_path = root / file_path

    if not full_path.exists():
        return {"error": f"文件不存在: {file_path}"}

    try:
        content = full_path.read_text()
        return {
            "file": file_path,
            "content": content,
            "lines": len(content.split('\n'))
        }
    except Exception as e:
        return {"error": str(e)}


def query_find_symbol(index: dict, symbol_name: str) -> dict:
    """查询: 查找符号定义"""
    results = []

    for layer, layer_data in index["structure"].items():
        for file in layer_data["files"]:
            if symbol_name in file["exports"]:
                results.append({
                    "layer": layer,
                    "file": file["name"],
                    "path": file["path"],
                    "symbol": symbol_name,
                    "type": "export"
                })

    return {
        "symbol": symbol_name,
        "found": len(results) > 0,
        "locations": results
    }


def execute_query(index: dict, project_root: str, query: str) -> dict:
    """执行查询"""
    if query.startswith("list_files:"):
        layer = query.split(":", 1)[1]
        return query_list_files(index, layer)

    elif query.startswith("read_file:"):
        file_path = query.split(":", 1)[1]
        return query_read_file(index, project_root, file_path)

    elif query.startswith("find_symbol:"):
        symbol = query.split(":", 1)[1]
        return query_find_symbol(index, symbol)

    else:
        return {"error": f"未知查询类型: {query}"}


def main():
    if len(sys.argv) < 4:
        print("Usage: python search_in_module.py <project_root> <module_name> <query>")
        print()
        print("Query types:")
        print("  list_files:<layer>")
        print("  read_file:<layer>/<file>")
        print("  find_symbol:<symbol_name>")
        sys.exit(1)

    project_root = sys.argv[1]
    module_name = sys.argv[2]
    query = sys.argv[3]

    try:
        index = load_module_index(project_root, module_name)
        result = execute_query(index, project_root, query)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
