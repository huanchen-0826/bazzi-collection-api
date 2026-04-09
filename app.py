# 文件名: app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # 允许跨域，防止前端报错
from baazi_core import get_baazi_data # 导入刚才那个核心文件
import json
import os
import urllib.request

app = Flask(__name__)
CORS(app) # 开启跨域支持

# SUPABASE configuration
supabase_url = os.environ.get('supabase_url', 'https://zxzbkpmholwhbxmmlufy.supabase.co')
supabase_key = os.environ.get('supabase_key', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emJrcG1ob2x3aGJ4bW1sdWZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3Mzc2MTgsImV4cCI6MjA5MTMxMzYxOH0.yXfWqBK0S3T2efyFtbW-bMFDuy4hOigMabTZHfEz3b0')

def save_to_supabase(data):
    """Save data into Supabase"""
    url = f"{supabase_url}/rest/v1/readings"

    payload = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('apikey', supabase_key)
    req.add_header('Authorization', f'Bearer {supabase_key}')
    req.add_header('Prefer', 'return=minimal')

    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"Save failed: {e}")
        return False

# 定义一个接口，比如叫 /api/calculate
@app.route('/api/calculate', methods=['POST'])
def calculate():
    # 1. 接收前端传来的 JSON 数据
    data = request.get_json()
    
    # 简单的容错
    if not data:
        return jsonify({"error": "没有收到数据"}), 400
        
    try:
        # 2. 提取参数
        name = data.get('name')
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        hour = int(data.get('hour'))
        minute = int(data.get('minute', 0))
        gender = data.get('gender', '未填写')
        
        # 3. 调用我们的核心逻辑 (厨房做菜)
        result = get_baazi_data(year, month, day, hour, minute, gender)

        # 4. 存储到数据库
        save_to_supabase({
            "customer_name": name,
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
            "birth_hour": hour,
            "birth_minute": minute,
            "gender": gender,
            "bazzi_result": json.dumps(result['bazi'], ensure_ascii=False)
        })
        
        # 5. 返回结果给前端
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 启动服务器
import os

if __name__ == '__main__':
    # print("服务已启动：http://127.0.0.1:5000")
    port = int(os.environ.get('PORT', 5000))
    # app.run(debug=True, port=5000)
    app.run(host='0.0.0.0', port=port)