# 文件名: baazi_core.py
# -*- coding: utf-8 -*-
import sys
from lunar_python import Solar
import matplotlib
matplotlib.use('Agg')  # 必须在 import pyplot 之前设置
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64
import os
import requests

# 字体文件的绝对路径（模块级别缓存，只算一次）
_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font.otf')
_FONT_PROP = None  # 全局 FontProperties 对象，避免每次重建

def _init_font():
    """初始化字体，返回 FontProperties 对象（直接用文件路径，绕过字体缓存）"""
    global _FONT_PROP
    if os.path.exists(_FONT_PATH):
        _FONT_PROP = fm.FontProperties(fname=_FONT_PATH)
        print(f"[FONT] 字体文件找到: {_FONT_PATH}", flush=True)
    else:
        _FONT_PROP = None
        print(f"[FONT] 警告：字体文件不存在: {_FONT_PATH}", flush=True)

_init_font()

def get_baazi_data(year, month, day, hour, minute, gender):
    """
    输入：出生时间
    输出：一个包含所有分析结果的字典 (Dictionary)
    """
    # 1. 计算八字
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    baazi = lunar.getEightChar()

    # 获取四柱
    pillars = [baazi.getYear(), baazi.getMonth(), baazi.getDay(), baazi.getTime()]

    # 2. 统计五行
    wuxing_map = {
        '甲': '木', '乙': '木', '寅': '木', '卯': '木',
        '丙': '火', '丁': '火', '巳': '火', '午': '火',
        '戊': '土', '己': '土', '辰': '土', '戌': '土', '丑': '土', '未': '土',
        '庚': '金', '辛': '金', '申': '金', '酉': '金',
        '壬': '水', '癸': '水', '子': '水', '亥': '水'
    }
    stats = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    chars = []

    for p in pillars:
        chars.append(p[0])
        chars.append(p[1])

    for char in chars:
        ele = wuxing_map.get(char)
        if ele: stats[ele] += 1

    # 3. 统计藏干
    canggan_map = {
        '子': ['癸'],
        '丑': ['己', '癸', '辛'],
        '寅': ['甲', '丙', '戊'],
        '卯': ['乙'],
        '辰': ['戊', '乙', '癸'],
        '巳': ['丙', '戊', '庚'],
        '午': ['丁', '己'],
        '未': ['己', '丁', '乙'],
        '申': ['庚', '壬', '戊'],
        '酉': ['辛'],
        '戌': ['戊', '辛', '丁'],
        '亥': ['壬', '甲']
    }
    # TO-DO

    # 4. 十神计算
    shishen_map = {
        ('甲','甲'):('比肩'),('甲','乙'):('劫财'),
        ('甲','丙'):('食神'),('甲','丁'):('伤官'),
        ('甲','戊'):('偏财'),('甲','己'):('正财'),
        ('甲','庚'):('七杀'),('甲','辛'):('正官'),
        ('甲','壬'):('偏印'),('甲','癸'):('正印'),
        # TO-DO
    }

    def get_shi_shen(day_master, gan):
        return shishen_map.get((day_master, gan), '未知')

    # 5. 排大运
    gender_int = 1 if gender == 'male' else 0
    dayun = baazi.getYun(gender_int)

    # 6. 生成图片并转为 Base64 字符串
    img_base64 = generate_chart_base64(stats)

    # 7. 简单的日主和财星逻辑
    day_master = chars[4]
    day_master_element = wuxing_map[day_master]

    # 这是一个简单的数据包，这就是我们要卖给前端的"产品"
    result = {
        "bazi": pillars, # ['己巳', '壬申'...]
        "day_master": day_master,
        "day_master_element": day_master_element,
        "wuxing_stats": stats,
        "chart_image": img_base64  # 图片在这里！
    }
    return result

def generate_chart_base64(stats):
    """
    画图，不弹窗，保存成字符串。
    关键：用 FontProperties(fname=...) 直接给每个文字对象赋字体，
    完全绕过 matplotlib 的字体注册表和缓存。
    """
    elements = list(stats.keys())
    counts = list(stats.values())
    colors = ['#E6B422', '#2E8B57', '#4682B4', '#CD5C5C', '#D2691E']

    fig, ax = plt.subplots(figsize=(6, 4))

    # 画饼图，获取 text 对象列表
    wedges, label_texts, autotext_labels = ax.pie(
        counts,
        labels=elements,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='w')
    )

    # 中心文字
    center_text = ax.text(0, 0, '五行\n能量',
                          ha='center', va='center',
                          fontsize=12, fontweight='bold')

    # 标题
    title_obj = ax.set_title('八字能量结构', fontsize=14)

    # 关键：如果字体文件存在，直接把 FontProperties 赋给每个文字对象
    # 这样完全不依赖字体名称查找，100% 可靠
    if _FONT_PROP is not None:
        for t in label_texts:
            t.set_fontproperties(_FONT_PROP)
        for t in autotext_labels:
            t.set_fontproperties(_FONT_PROP)
        center_text.set_fontproperties(_FONT_PROP)
        ax.title.set_fontproperties(_FONT_PROP)
        print("[FONT] 字体已成功应用到图表", flush=True)
    else:
        print("[FONT] 警告：字体未加载，中文可能显示为方块", flush=True)

    plt.tight_layout()

    # 保存到内存缓冲区
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)

    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()

    return img_str
