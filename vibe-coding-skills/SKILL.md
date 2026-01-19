---
name: vibe-coding-skills
description: "安装 vibe 开发套件（vibe-coding 规范文件集）到目标项目目录：当用户说“安装vibe开发套件 / 安装 vibe 开发套件 / 安装 vibe-coding 规范 / 把 CodeSkills 规范拷贝到项目”时使用。该 skill 会运行内置脚本，将 `AGENTS.md`、`context/`、`skills/`、`requirements/README.md` 等 kit 文件复制到目标项目根目录，并提供校验与自动化冒烟用例。"
---

# 安装 vibe 开发套件（vibe-coding-skills）

- 宣告：使用 `vibe-coding-skills` 安装 vibe 开发套件（kit）。
- 目标：把本 skill 内置的 kit 文件复制到目标项目根目录，使项目立刻具备 `AGENTS.md` 约束、`context/*` 上下文模板、`skills/*` 工作流与 `requirements/README.md` 说明。

## 1) 收集必要输入

- **目标项目根目录**：优先让用户明确给出绝对路径；若用户未给，可默认当前工作目录（但要在输出中明确你将写入哪个目录）。
- **覆盖策略**：
  - 默认：不覆盖目标目录中已存在的同名文件（安全、幂等）。
  - 需要覆盖：使用 `--force`（覆盖前会备份已存在文件，并写入安装日志）。
- **可选：dry-run**：用户不确定影响范围时，用 `--dry-run` 先预览动作。

## 2) 执行安装

运行：

`bash skills/vibe-coding-skills/scripts/install.sh <target-dir> [--force] [--dry-run]`

输出约定：
- 安装备份：`<target-dir>/.vibe-kit-backups/<timestamp>/...`
- 安装日志：`<target-dir>/.vibe-kit-install/logs/<timestamp>.log`

## 3) 校验安装结果

运行：

`bash skills/vibe-coding-skills/scripts/validate.sh <target-dir>`

- 校验失败时：把缺失项逐条列出，并停止后续“开始开发”的建议（先修复安装/路径问题）。

## 4) 自动化冒烟（仓库内自测）

运行：

`bash skills/vibe-coding-skills/scripts/smoke.sh`

该冒烟会在临时目录执行：默认安装（两次幂等）+ `--force` 覆盖（生成备份与日志）+ 校验。

## 5) 维护说明（kit snapshot）

- kit 内容位于 `skills/vibe-coding-skills/assets/kit/`，是一个可分发的 snapshot。
- 当本仓库 `AGENTS.md` / `context/` / `skills/` / `requirements/README.md` 发生变化时，需要同步更新 kit（避免安装到目标项目的规范过期）。
