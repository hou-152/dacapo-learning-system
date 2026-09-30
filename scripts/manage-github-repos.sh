#!/bin/bash

# GitHub 仓库统一管理脚本
# 用途：批量为仓库添加 Release、更新 README、归档项目

set -e

echo "=== GitHub 仓库统一管理工具 ==="
echo ""

# 检查 gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 需要安装 GitHub CLI (gh)"
    exit 1
fi

# 检查认证
if ! gh auth status &> /dev/null; then
    echo "❌ 请先登录 GitHub CLI: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI 已认证"
echo ""

# 功能菜单
echo "请选择操作："
echo "1. 列出所有仓库"
echo "2. 为主要项目添加 Release"
echo "3. 归档不活跃项目"
echo "4. 查看仓库统计"
echo "5. 批量更新 README（添加归档声明）"
echo ""

read -p "输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "=== 所有仓库 ==="
        gh repo list hou-152 --limit 50 --json name,isPrivate,updatedAt --jq '.[] | "\(.name) | \(if .isPrivate then "private" else "public" end) | \(.updatedAt)"'
        ;;

    2)
        echo ""
        echo "=== 为主要项目添加 Release ==="
        echo ""

        # skill-adapter
        echo "1. skill-adapter"
        read -p "   创建 v1.0.0 release? (y/n): " create_release
        if [ "$create_release" = "y" ]; then
            cd ~/Documents/skill-adapter 2>/dev/null || echo "   ⚠️  目录不存在"
            git tag -a v1.0.0 -m "skill-adapter v1.0.0" 2>/dev/null || echo "   ⚠️  标签可能已存在"
            git push origin v1.0.0 2>/dev/null || echo "   ⚠️  推送失败"
            gh release create v1.0.0 --title "skill-adapter v1.0.0" --notes "首次发布" 2>/dev/null || echo "   ⚠️  Release 可能已存在"
            echo "   ✅ 完成"
        fi

        echo ""
        echo "2. fitness-family"
        read -p "   创建 v1.0.0 release? (y/n): " create_release
        if [ "$create_release" = "y" ]; then
            cd ~/Documents/fitness-family 2>/dev/null || echo "   ⚠️  目录不存在"
            git tag -a v1.0.0 -m "fitness-family v1.0.0" 2>/dev/null || echo "   ⚠️  标签可能已存在"
            git push origin v1.0.0 2>/dev/null || echo "   ⚠️  推送失败"
            gh release create v1.0.0 --title "fitness-family v1.0.0" --notes "首次发布" 2>/dev/null || echo "   ⚠️  Release 可能已存在"
            echo "   ✅ 完成"
        fi
        ;;

    3)
        echo ""
        echo "=== 归档不活跃项目 ==="
        echo ""
        echo "以下项目超过 6 个月未更新："
        gh repo list hou-152 --limit 50 --json name,updatedAt --jq '.[] | select(.updatedAt < "2026-03-30") | .name'
        echo ""
        read -p "输入要归档的仓库名（空格分隔）: " repos

        for repo in $repos; do
            echo "归档: $repo"
            gh repo archive "hou-152/$repo" --yes 2>/dev/null && echo "✅ $repo 已归档" || echo "❌ $repo 归档失败"
        done
        ;;

    4)
        echo ""
        echo "=== 仓库统计 ==="
        echo ""

        total=$(gh repo list hou-152 --limit 50 --json name | jq '. | length')
        public=$(gh repo list hou-152 --limit 50 --json isPrivate | jq '[.[] | select(.isPrivate == false)] | length')
        private=$(gh repo list hou-152 --limit 50 --json isPrivate | jq '[.[] | select(.isPrivate == true)] | length')

        echo "总仓库数: $total"
        echo "公开仓库: $public"
        echo "私有仓库: $private"
        echo ""

        echo "按最后更新时间分组："
        echo "近 7 天: $(gh repo list hou-152 --limit 50 --json updatedAt | jq '[.[] | select(.updatedAt > "2026-09-23")] | length')"
        echo "近 30 天: $(gh repo list hou-152 --limit 50 --json updatedAt | jq '[.[] | select(.updatedAt > "2026-08-30")] | length')"
        echo "超过 3 个月: $(gh repo list hou-152 --limit 50 --json updatedAt | jq '[.[] | select(.updatedAt < "2026-06-30")] | length')"
        ;;

    5)
        echo ""
        echo "=== 批量更新 README ==="
        echo ""
        echo "功能：在归档项目的 README 顶部添加归档声明"
        echo ""
        read -p "输入要更新的仓库名（空格分隔）: " repos

        for repo in $repos; do
            echo "更新: $repo"

            # 克隆仓库（如果本地不存在）
            if [ ! -d "/tmp/$repo" ]; then
                gh repo clone "hou-152/$repo" "/tmp/$repo" 2>/dev/null || continue
            fi

            cd "/tmp/$repo"

            # 在 README 顶部添加归档声明
            if [ -f "README.md" ]; then
                echo "> ⚠️ **归档通知**: 此项目已归档，不再维护。请参考 [dacapo-learning-system](https://github.com/hou-152/dacapo-learning-system) 了解最新项目。" > /tmp/archive-notice.md
                echo "" >> /tmp/archive-notice.md
                cat README.md >> /tmp/archive-notice.md
                mv /tmp/archive-notice.md README.md

                git add README.md
                git commit -m "docs: 添加归档通知"
                git push origin main
                echo "✅ $repo 已更新"
            else
                echo "⚠️  $repo 没有 README.md"
            fi

            cd -
        done
        ;;

    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "=== 完成 ==="
