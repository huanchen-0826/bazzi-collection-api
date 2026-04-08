# 文件名: app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # 允许跨域，防止前端报错
from baazi_core import get_baazi_data # 导入刚才那个核心文件

app = Flask(__name__)
CORS(app) # 开启跨域支持

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
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        hour = int(data.get('hour'))
        minute = int(data.get('minute', 0))
        
        # 3. 调用我们的核心逻辑 (厨房做菜)
        result = get_baazi_data(year, month, day, hour, minute)
        
        # 4. 返回结果给前端
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