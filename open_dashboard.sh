#!/bin/bash
# DaCapo 学习中心快捷启动脚本

DASHBOARD_DIR="$HOME/Documents/dacapo-学习仓库/dashboard"

echo "🎓 启动 DaCapo 学习中心..."
echo ""
echo "可用页面："
echo "  1. 学习中心首页"
echo "  2. 概念网络图"
echo "  3. 学习进度仪表盘"
echo ""

if [ "$1" == "network" ]; then
    open "$DASHBOARD_DIR/network.html"
    echo "✅ 已打开概念网络图"
elif [ "$1" == "progress" ]; then
    open "$DASHBOARD_DIR/progress.html"
    echo "✅ 已打开学习进度仪表盘"
else
    open "$DASHBOARD_DIR/index.html"
    echo "✅ 已打开学习中心首页"
fi
