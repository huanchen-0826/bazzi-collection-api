# 文件名: baazi_core.py
# -*- coding: utf-8 -*-
from lunar_python import Solar
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64
import os
import requests

# 设置 matplotlib 后端为 'Agg'，这样它不会尝试弹窗，而是静默画图
plt.switch_backend('Agg')

# 配置字体（保持之前的逻辑）
plt.style.use('bmh')

def configure_fonts():
    import os
    from matplotlib import font_manager
    
    # 字体文件和代码在同一目录
    font_path = os.path.join(os.path.dirname(__file__), 'font.otf')
    
    if os.path.exists(font_path):
        font_manager.fontManager.addfont(font_path)
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC']
        plt.rcParams['axes.unicode_minus'] = False
        print(f"字体加载成功: {font_path}")
    else:
        print(f"字体文件不存在: {font_path}")

configure_fonts()

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
    
    # 这是一个简单的数据包，这就是我们要卖给前端的“产品”
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
    画图，但是不弹窗，而是保存成字符串
    """
    elements = list(stats.keys())
    counts = list(stats.values())
    colors = ['#E6B422', '#2E8B57', '#4682B4', '#CD5C5C', '#D2691E']
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(counts, labels=elements, autopct='%1.1f%%', startangle=90, colors=colors,
           wedgeprops=dict(width=0.4, edgecolor='w'))
    ax.text(0, 0, '五行\n能量', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.set_title('八字能量结构', fontsize=14)
    plt.tight_layout()
    
    # --- 关键步骤：保存到内存 ---
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    
    # 转成 base64 字符串 (这样图片就可以像文字一样传输了)
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close() # 关掉画布，释放内存
    
    return img_str