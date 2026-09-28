# -*- coding: utf-8 -*-
"""社会学基本概念复习图：13 概念总览 + 已学 7 概念关系网络。
Guizang 风格近似：off-white 底、黑描边、单一 IKB 蓝 accent、短标签。"""
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
OUT_DIR = '/Users/housibo/Documents/dbskill-learning/社会学基本概念/assets/13概念复习图'

OFFWHITE = (246, 244, 239)
INK = (20, 20, 20)
GRAY = (118, 116, 110)
DARKGRAY = (60, 58, 54)
BLUE = (0, 47, 167)   # IKB Blue #002FA7
WHITE = (255, 255, 255)
BADGE_GRAY = (150, 148, 142)


def font(sz):
    return ImageFont.truetype(FONT_PATH, sz)


def bold(d, xy, s, f, fill=INK):
    d.text(xy, s, font=f, fill=fill, stroke_width=1, stroke_fill=fill)


def label_pill(d, cx, cy, text, fsize=21):
    """白底圆角胶囊 + 蓝字，居中于 (cx, cy)。"""
    f = font(fsize)
    tw = d.textlength(text, font=f)
    pad = 10
    w, h = tw + pad * 2, fsize + 16
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=h / 2, fill=WHITE, outline=BLUE, width=2)
    d.text((cx - tw / 2, cy - fsize / 2 - 1), text, font=f, fill=BLUE,
           stroke_width=1, stroke_fill=BLUE)


def arrow(d, p1, p2, width=4, dashed=False):
    import math
    x1, y1 = p1
    x2, y2 = p2
    if dashed:
        # 手绘虚线
        seg = 14
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        n = int(dist // (seg * 2))
        for i in range(n + 1):
            t0 = i * 2 * seg / dist
            t1 = min((i * 2 + 1) * seg / dist, 1.0)
            d.line([x1 + dx * t0, y1 + dy * t0, x1 + dx * t1, y1 + dy * t1],
                   fill=BLUE, width=width)
    else:
        d.line([x1, y1, x2, y2], fill=BLUE, width=width)
    # 箭头三角
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 16
    a1 = ang + math.radians(158)
    a2 = ang - math.radians(158)
    d.polygon([(x2, y2),
               (x2 + L * math.cos(a1), y2 + L * math.sin(a1)),
               (x2 + L * math.cos(a2), y2 + L * math.sin(a2))],
              fill=BLUE)


def concept_card(d, x, y, w, h, title, subtitle, accent=True):
    d.rounded_rectangle([x, y, x + w, y + h], 14, fill=WHITE,
                        outline=INK, width=2)
    d.rounded_rectangle([x, y, x + 10, y + h], 14,
                        fill=BLUE if accent else BADGE_GRAY)
    tx = x + 26
    bold(d, (tx, y + 12), title, font(30), fill=INK)
    for i, line in enumerate(subtitle.split('\n')):
        d.text((tx, y + 52 + i * 30), line, font=font(21), fill=DARKGRAY)


# ============ 图 1：13 概念总览 ============
W, H = 1600, 1000
img = Image.new('RGB', (W, H), OFFWHITE)
d = ImageDraw.Draw(img)

bold(d, (60, 44), '社会学基本概念 · 13 个核心概念总览', font(46), fill=INK)
d.rounded_rectangle([60, 106, 224, 116], 5, fill=BLUE)
bold(d, (60, 126), '主题一 · 社会学的思维方式', font(30), fill=BLUE)
bold(d, (840, 126), '主题二 · 社会学研究方法', font(30), fill=BLUE)

left = [
    ('01', '社会', 'Society', '有边界：共享文化制度、相互依赖、代代延续', True),
    ('02', '结构 / 能动', 'Structure / Agency', '结构是行动的中介，也是行动的结果', True),
    ('03', '理性化', 'Rationalization', '可计算、可预测、效率至上；铁笼与去魅', True),
    ('04', '话语', 'Discourse', '说话塑造现实；说法分配责任', True),
    ('05', '全球化', 'Globalization', '世界范围的联系越来越紧密', False),
    ('06', '现代性', 'Modernity', '工业化、理性化塑造的社会形态', False),
    ('07', '后现代性', 'Postmodernity', '对宏大叙事的怀疑与多元并存', False),
]
right = [
    ('08', '理想类型', 'Ideal Type', '概念是量尺，现实总在偏离它', True),
    ('09', '反身性', 'Reflexivity', '观察者把自己也放进画面', True),
    ('10', '社会建构论', 'Social Constructionism', '现实靠共识、制度、日常重复建出来', True),
    ('11', '定性 / 定量', 'Qual / Quant', '深度理解 vs 数字测量', False),
    ('12', '唯实论', 'Realism', '现实独立于我们对它的说法存在', False),
    ('13', '科学', 'Science', '用系统方法生产可靠知识', False),
]


def draw_card(d, x, y, w, h, num, name, en, desc, learned):
    d.rounded_rectangle([x, y, x + w, y + h], 14, fill=WHITE,
                        outline=INK, width=2)
    d.rounded_rectangle([x, y, x + 10, y + h], 14,
                        fill=BLUE if learned else BADGE_GRAY)
    bold(d, (x + 26, y + 8), num, font(28), fill=BLUE if learned else BADGE_GRAY)
    bold(d, (x + 84, y + 6), name, font(30), fill=INK)
    d.text((x + 84, y + 42), en, font=font(18), fill=GRAY)
    d.text((x + 26, y + 72), desc, font=font(21), fill=DARKGRAY)
    # 已学/待学 badge
    bw = 64
    bx, by = x + w - bw - 14, y + 10
    if learned:
        d.rounded_rectangle([bx, by, bx + bw, by + 26], 13, fill=BLUE)
        d.text((bx + 15, by + 4), '已学', font=font(16), fill=WHITE)
    else:
        d.rounded_rectangle([bx, by, bx + bw, by + 26], 13, fill=BADGE_GRAY)
        d.text((bx + 15, by + 4), '待学', font=font(16), fill=WHITE)


card_h, gap, y0 = 96, 10, 168
for i, c in enumerate(left):
    draw_card(d, 60, y0 + i * (card_h + gap), 700, card_h, *c)
for i, c in enumerate(right):
    draw_card(d, 840, y0 + i * (card_h + gap), 700, card_h, *c)

d.text((60, 945), '蓝条 = 课程 01-12 已覆盖 · 灰条 = 书中概念待学（其余已学概念见「概念三层网络图」）',
       font=font(20), fill=GRAY)
img.save(f'{OUT_DIR}/13概念总览图.png')
print('总览图 done')

# ============ 图 2：已学 7 概念关系网络 ============
img2 = Image.new('RGB', (W, H), OFFWHITE)
d = ImageDraw.Draw(img2)

bold(d, (60, 44), '概念关系网络 · 已学 7 概念怎么咬合', font(46), fill=INK)
d.rounded_rectangle([60, 106, 224, 116], 5, fill=BLUE)
d.text((60, 124), '每个箭头标签 = 该箭头的含义', font=font(22), fill=GRAY)

# 中心轴心卡
concept_card(d, 620, 400, 360, 160, '结构 / 能动', '轴心：结构约束行动\n行动再生产结构')
# 左侧：社会
concept_card(d, 100, 400, 360, 160, '社会', '有边界；靠共享规则\n与资源维系')
# 右侧三卡
concept_card(d, 1060, 150, 400, 150, '理性化', '可计算、可预测的\n高密度形态')
concept_card(d, 1060, 400, 400, 150, '话语', '语言层：说法分配责任\n塑造现实')
concept_card(d, 1060, 650, 400, 150, '社会建构论', '三种建法：命名 + 制度化\n+ 日常重复')

# 箭头
arrow(d, (460, 480), (620, 480))                    # 社会 -> 结构/能动
label_pill(d, 528, 442, '规则 + 资源')
arrow(d, (980, 435), (1060, 225))                   # 中心 -> 理性化
label_pill(d, 1018, 352, '高密度形态')
arrow(d, (980, 480), (1060, 475))                   # 中心 -> 话语
label_pill(d, 1018, 442, '语言层')
arrow(d, (980, 525), (1060, 725))                   # 中心 -> 社会建构论
label_pill(d, 1018, 588, '三种建法')

# 底部工具框（虚线）
d.rounded_rectangle([100, 770, 980, 960], 16, fill=(250, 249, 245),
                    outline=BLUE, width=3)
bold(d, (128, 786), '研究工具箱 · 量尺与镜子', font(26), fill=BLUE)
concept_card(d, 130, 826, 400, 110, '理想类型', '量尺：拿现实和纯形态比')
concept_card(d, 550, 826, 400, 110, '反身性', '镜子：把自己放进画面')
# 工具框 -> 中心卡（虚线）
arrow(d, (540, 770), (540, 560), dashed=True)
label_pill(d, 450, 664, '怎么测量自己')

img2.save(f'{OUT_DIR}/概念关系网络图.png')
print('网络图 done')

# ============ 图 3：12 概念三层网络（工具 → 结构 → 人） ============
img3 = Image.new('RGB', (W, H), OFFWHITE)
d = ImageDraw.Draw(img3)

bold(d, (60, 44), '概念三层网络 · 已学 12 概念', font(46), fill=INK)
d.rounded_rectangle([60, 106, 224, 116], 5, fill=BLUE)
d.text((60, 124), '工具（怎么看）→ 结构（社会怎么运转）→ 人（结构落进人）', font=font(22), fill=GRAY)


def layer_box(d, x, y, w, h, title):
    d.rounded_rectangle([x, y, x + w, y + h], 16, fill=(250, 249, 245),
                        outline=INK, width=2)
    bold(d, (x + 18, y + 12), title, font(26), fill=BLUE)


# 工具层
layer_box(d, 60, 140, 1480, 160, '工具层 · 怎么看')
concept_card(d, 100, 176, 380, 100, '社会学的想象力', '变焦：个人困扰 ↔ 公共议题')
concept_card(d, 610, 176, 380, 100, '理想类型', '量尺：现实总在偏离纯形态')
concept_card(d, 1120, 176, 380, 100, '反身性', '镜子：把自己放进画面')

# 结构层
layer_box(d, 60, 330, 1480, 330, '结构层 · 社会怎么运转')
concept_card(d, 100, 368, 380, 110, '社会', '有边界；规则与资源')
concept_card(d, 610, 368, 380, 110, '结构 / 能动', '轴心：结构二重性')
concept_card(d, 100, 512, 380, 110, '理性化', '可计算、可预测的高密度形态')
concept_card(d, 610, 512, 380, 110, '话语', '语言层：说法分配责任')
concept_card(d, 1120, 512, 380, 110, '社会建构论', '三种建法的合体')

# 人层
layer_box(d, 60, 690, 1480, 250, '人层 · 结构落进人')
concept_card(d, 100, 728, 330, 105, '社会化', '规则进入人')
concept_card(d, 470, 728, 330, 105, '风险', '命名 · 测量 · 分配')
concept_card(d, 840, 728, 330, 105, '异化', '造物反噬造物主')
concept_card(d, 1210, 728, 300, 105, '可持续发展', '代价分配')

# 结构层内部箭头
arrow(d, (480, 423), (610, 423))                      # 社会 -> 结构/能动
label_pill(d, 530, 398, '规则与资源')
arrow(d, (700, 478), (430, 512))                      # 结构/能动 -> 理性化
label_pill(d, 548, 498, '高密度形态')
arrow(d, (800, 478), (800, 512))                      # 结构/能动 -> 话语
label_pill(d, 862, 497, '语言层')
arrow(d, (990, 478), (1200, 512))                     # 结构/能动 -> 社会建构论
label_pill(d, 1096, 498, '日常重复')
arrow(d, (990, 567), (1120, 567))                     # 话语 -> 社会建构论
label_pill(d, 1055, 542, '命名')

# 层间箭头
arrow(d, (1330, 622), (1000, 728))                    # 社会建构论 -> 风险
label_pill(d, 1145, 668, '分配')
arrow(d, (240, 622), (960, 728), dashed=True)         # 理性化 -.-> 异化
label_pill(d, 580, 668, '铁笼之后')
# 人层内部
arrow(d, (1170, 780), (1210, 780))                    # 风险 -> 可持续发展
label_pill(d, 1100, 800, '代价分配')

d.text((60, 950), '工具层三台设备（变焦 / 量尺 / 镜子）适用于全部概念，虚线边见 12.md 的 Mermaid 图',
       font=font(20), fill=GRAY)
img3.save(f'{OUT_DIR}/概念三层网络图.png')
print('三层网络图 done')
