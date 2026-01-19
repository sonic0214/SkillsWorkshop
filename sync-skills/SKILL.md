---
name: sync-skills
description: Diff and synchronize skill folders across multiple locations (typically `.factory/skills`, `~/.claude/skills`, and `~/.codex/skills` / `$CODEX_HOME/skills`) so every location has the same full set and identical contents. Use when the user says “同步skill/同步skills”, “sync skills”, “把skills同步到各个地方”, or asks to compare/merge skills directories.
---

# Sync Skills

运行 `scripts/sync_skills.py` 自动发现多个 skill 根目录，做差异对比并把所有 skills 同步到每个地方，最后做一致性校验（确保大家都是全集且内容一致）。

## 快速使用

- 预览（只看差异，不改文件）：
  - `python3 scripts/sync_skills.py`
- 同步并校验（推荐用于“同步skill”指令）：
  - `python3 scripts/sync_skills.py --apply`

## 发现规则（默认）

脚本会尽量自动找到这些位置：

- `~/.factory/skills`（Factory 的 skills 主目录；推荐使用这个）
- 当前目录及其父目录中的 `.factory/skills`
- `~/.claude/skills`（Claude 的 skills）
- `~/.codex/skills`（或 `$CODEX_HOME/skills`）

如需显式指定根目录，用 `--roots /a/b/.factory/skills /c/d/skills`。

## 冲突处理（同名 skill 内容不同）

默认策略：选择“最新修改”的那个版本作为源（按该 skill 目录内文件的最大 mtime 计算），并把它同步到其它地方；脚本会在输出中标记冲突并给出可复现的 `diff -ru` 命令。

## 配置（可选）

可创建配置文件固定 root 列表与策略：

- `~/.codex/skill-sync/config.json`（或 `$CODEX_HOME/skill-sync/config.json`）

示例：

```json
{
  "roots": ["/abs/path/to/.factory/skills", "/Users/me/.codex/skills"],
  "prefer": "newest"
}
```
