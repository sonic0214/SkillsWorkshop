---
name: ai-info-stream-collector
description: Collect and update AI/news articles from configured RSS/API/web sources, optionally translate titles to Chinese, and store results in the KnowledgeSystem DB/JSON. Use when the user asks to run or schedule the AI资讯抓取/信息流更新, adjust sources or translation settings, or verify saved outputs.
---

# AI Info Stream Collector

## Overview

Run the crawler in `/Users/admin/.claude/skills/ai-info-stream-collector/ai-info-stream-collector-code` to fetch new articles incrementally, translate titles when enabled, and save results to the KnowledgeSystem storage path.

## Quick Start

### Run once

```bash
cd /Users/admin/.claude/skills/ai-info-stream-collector/ai-info-stream-collector-code
python3 main.py --once
```

### Start scheduler

```bash
cd /Users/admin/.claude/skills/ai-info-stream-collector/ai-info-stream-collector-code
python3 main.py
```

## Configuration

- `config.yaml` is the active config used by the collector.
- To use full sources, copy `config_full.yaml` over `config.yaml`.
- For fast checks, copy `config_test.yaml` over `config.yaml`.
- Update `translation.enabled`, `translation.target_language`, and `schedule.*` as needed.
- Edit `sources` to add/remove feeds or adjust `max_items`.
- Storage paths live under `storage.output_file` and `storage.database`.

## Outputs

- Articles are stored at:
  - `/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/articles.db`
  - `/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/articles.json`
- Review recent stats:

```bash
cd /Users/admin/.claude/skills/ai-info-stream-collector/ai-info-stream-collector-code
python3 view_articles.py
```

## Troubleshooting

- If translation is slow or rate-limited, set `translation.enabled: false` and rerun.
- If sources fail, remove them or lower `max_items` and rerun.
- The scheduler reads `config.yaml`; update that file before starting a scheduled run.
