#!/bin/bash
# 测试 analyze_existing_project.py

echo "=========================================="
echo "  VibeKit - analyze_existing_project.py"
echo "  测试脚本"
echo "=========================================="
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法：./test_analyze.sh <项目路径>"
    echo ""
    echo "示例："
    echo "  ./test_analyze.sh ~/my-project"
    echo "  ./test_analyze.sh ."
    echo ""
    exit 1
fi

PROJECT_PATH=$1

# 检查项目路径
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ 项目路径不存在：$PROJECT_PATH"
    exit 1
fi

echo "✅ 项目路径：$PROJECT_PATH"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.7+"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 检查 graphviz
if ! python3 -c "import graphviz" &> /dev/null; then
    echo "⚠️  未安装 graphviz Python 包"
    echo "   安装：pip install graphviz"
    echo ""
    read -p "   是否现在安装? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install graphviz
    fi
fi

# 检查 graphviz 系统依赖
if ! command -v dot &> /dev/null; then
    echo "⚠️  未安装 graphviz 系统依赖"
    echo ""
    echo "   macOS:   brew install graphviz"
    echo "   Ubuntu:  sudo apt-get install graphviz"
    echo "   Windows: https://graphviz.org/download/"
    echo ""
    read -p "   继续运行分析？(可视化会失败) (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "开始分析..."
echo ""

# 运行分析
python3 analyze_existing_project.py "$PROJECT_PATH"

EXIT_CODE=$?

echo ""
echo "=========================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "  ✅ 分析完成，未发现循环依赖"
else
    echo "  ⚠️  分析完成，发现架构问题"
fi

echo "=========================================="
echo ""

# 打开报告
REPORT_PATH="$PROJECT_PATH/.vibekit/analysis_report.md"
if [ -f "$REPORT_PATH" ]; then
    echo "查看报告："
    echo "  cat $REPORT_PATH"
    echo ""

    # 尝试在默认编辑器中打开
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "在 macOS 中打开报告..."
        open "$REPORT_PATH"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "$REPORT_PATH"
        fi
    fi
fi

exit $EXIT_CODE
