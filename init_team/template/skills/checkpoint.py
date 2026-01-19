#!/usr/bin/env python3
"""checkpoint.py - 状态快照"""

import json
import sys
from datetime import datetime
from pathlib import Path


def save_checkpoint(project_root, phase_name):
    """保存检查点"""
    root = Path(project_root).resolve()
    checkpoints_dir = root / ".checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_id = f"{phase_name}_{timestamp}"

    state = {
        "checkpoint_id": checkpoint_id,
        "phase": phase_name,
        "timestamp": datetime.now().isoformat(),
        "context_pointers": {}
    }

    checkpoint_file = checkpoints_dir / f"{checkpoint_id}.json"
    checkpoint_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    latest_file = checkpoints_dir / "latest.json"
    latest_file.write_text(json.dumps({"checkpoint_id": checkpoint_id}, indent=2))

    print(f"✓ 检查点已保存: {checkpoint_id}")
    return checkpoint_id


def list_checkpoints(project_root):
    """列出检查点"""
    root = Path(project_root).resolve()
    checkpoints_dir = root / ".checkpoints"

    if not checkpoints_dir.exists():
        print("没有检查点")
        return

    checkpoints = []
    for file in checkpoints_dir.glob("*.json"):
        if file.name == "latest.json":
            continue
        data = json.loads(file.read_text())
        checkpoints.append(data)

    print(f"检查点列表 (共 {len(checkpoints)} 个):")
    for cp in checkpoints:
        print(f"  • {cp['checkpoint_id']} - {cp['phase']}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python checkpoint.py save|list <project_root> [phase_name]")
        sys.exit(1)

    command = sys.argv[1]
    project_root = sys.argv[2]

    if command == "save":
        phase_name = sys.argv[3] if len(sys.argv) > 3 else "default"
        save_checkpoint(project_root, phase_name)
    elif command == "list":
        list_checkpoints(project_root)
