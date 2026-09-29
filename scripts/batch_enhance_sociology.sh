#!/bin/bash
# 批量为社会学课程添加 DaCapo 即时反馈

COURSE_DIR="$HOME/Documents/dbskill-learning/社会学七书共读"

echo "📚 开始为社会学课程添加即时反馈..."
echo ""

# 01.md - 社会学想象力
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/01.md" 社会学想象力

# 02.md - 差序格局
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/02.md" 差序格局 礼治秩序

# 03.md - 已完成
echo "⏭️  03.md 已有反馈，跳过"

# 04.md - 社会分层
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/04.md" 社会分层 先赋vs自致 结构紧张

# 05.md - 再生产
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/05.md" 再生产 婚礼产品发布会

# 06.md - 公私界碑
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/06.md" 公私界碑 彩礼异化

# 07.md - 承认政治
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/07.md" 承认政治 人性三分法 承认与狂热

# 08.md - 理性化铁笼
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/08.md" 理性化铁笼 铁笼囚徒困境

# 09.md - 结课总结
python3 scripts/enhance_dbs_learning.py "$COURSE_DIR/09.md"

echo ""
echo "✅ 完成！所有文章已添加 DaCapo 即时反馈"
echo ""
echo "📊 查看你的学习进度："
echo "   python3 scripts/progress_tracker.py"
