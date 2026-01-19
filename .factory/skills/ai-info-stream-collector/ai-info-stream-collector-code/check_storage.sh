#!/bin/bash

echo "=== 文章存储检查 ==="
echo ""

STORAGE_DIR="/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流"

if [ -d "$STORAGE_DIR" ]; then
    echo "✅ 存储目录存在: $STORAGE_DIR"
    echo ""

    if [ -f "$STORAGE_DIR/articles.db" ]; then
        SIZE=$(ls -lh "$STORAGE_DIR/articles.db" | awk '{print $5}')
        echo "✅ 数据库文件: articles.db ($SIZE)"

        COUNT=$(sqlite3 "$STORAGE_DIR/articles.db" "SELECT COUNT(*) FROM articles;")
        echo "   文章总数: $COUNT"
    else
        echo "❌ 数据库文件不存在"
    fi

    echo ""

    if [ -f "$STORAGE_DIR/articles.json" ]; then
        SIZE=$(ls -lh "$STORAGE_DIR/articles.json" | awk '{print $5}')
        echo "✅ JSON文件: articles.json ($SIZE)"
    else
        echo "❌ JSON文件不存在"
    fi
else
    echo "❌ 存储目录不存在: $STORAGE_DIR"
fi

echo ""
echo "=== 配置检查 ==="
echo ""
echo "config.yaml 中的路径:"
grep "database:" config.yaml

echo ""
echo "=== 结束 ==="
