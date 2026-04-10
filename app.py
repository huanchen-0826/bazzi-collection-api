# 文件名: app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # 允许跨域，防止前端报错
from baazi_core import get_baazi_data # 导入刚才那个核心文件
import json
import os
import urllib.request
import urllib.error

app = Flask(__name__)
CORS(app) # 开启跨域支持

# SUPABASE configuration（从环境变量读取，不在代码里硬编码密钥）
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("[WARN] Supabase 环境变量未设置！请在 Render 的 Environment 里添加 SUPABASE_URL 和 SUPABASE_KEY", flush=True)

def save_to_supabase(data):
    """Save data into Supabase"""
    url = f"{supabase_url}/rest/v1/readings"

    print(f"[DB] 目标 URL: {url}", flush=True)
    print(f"[DB] Key 前10位: {supabase_key[:10] if supabase_key else 'None'}", flush=True)

    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('apikey', supabase_key)
    req.add_header('Authorization', f'Bearer {supabase_key}')
    req.add_header('Prefer', 'return=minimal')

    try:
        import ssl
        # 创建 SSL context，兼容某些云平台的证书环境
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print(f"[DB] 保存成功，状态码: {resp.status}", flush=True)
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"[DB] HTTPError {e.code}: {body}", flush=True)
        return False
    except urllib.error.URLError as e:
        print(f"[DB] URLError（网络问题）: {e.reason}", flush=True)
        return False
    except Exception as e:
        print(f"[DB] 未知错误: {type(e).__name__}: {e}", flush=True)
        return False

@app.route('/api/health', methods=['GET'])
def health():
    """快速诊断接口：检查 Supabase 是否可达"""
    import ssl
    test_url = f"{supabase_url}/rest/v1/readings?limit=1"
    req = urllib.request.Request(test_url)
    req.add_header('apikey', supabase_key)
    req.add_header('Authorization', f'Bearer {supabase_key}')
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            return jsonify({"status": "ok", "db": "connected", "http_status": resp.status})
    except urllib.error.HTTPError as e:
        return jsonify({"status": "ok", "db": f"http_error_{e.code}"}), 200
    except Exception as e:
        return jsonify({"status": "ok", "db": "unreachable", "error": str(e)}), 200


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
        db_saved = save_to_supabase({
            "customer_name": name,
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
            "birth_hour": hour,
            "birth_minute": minute,
            "gender": gender,
            "bazzi_result": json.dumps(result['bazi'], ensure_ascii=False)
        })

        # 5. 返回结果给前端（db_saved 字段可帮助调试数据库是否写入成功）
        return jsonify({
            "status": "success",
            "db_saved": db_saved,
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