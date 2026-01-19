# Architecture

## 1. 总览
- 系统边界：本仓库是“规范与技能包”，不包含业务应用代码；通过拷贝/分发文件被其它项目复用。
- 关键模块：
  - `AGENTS.md`：项目协作与交付门槛
  - `context/`：上下文事实、架构与决策
  - `skills/`：可复用工作流（requirements 模板、各阶段技能）
  - `requirements/`：按 feature 沉淀业务产物（spec/design/review/tasks/status/changes）

## 2. 关键数据流
- 入口：用户在目标项目中触发“安装 vibe 开发套件”指令。
- 处理链路：安装脚本将 kit 文件复制到目标项目根目录，并生成安装日志/验收结果。
- 落库/输出：目标项目中的 `AGENTS.md`、`context/*`、`skills/*` 以及（可选）`requirements/README.md`。

## 3. 代码结构说明
- 目录约定：skills 以 `skills/<skill-name>/SKILL.md` 为入口，可包含 `scripts/` 与 `assets/`。
- 模块依赖：安装脚本仅依赖本地 shell 工具（优先 `rsync`，兼容 `cp` 兜底）。

