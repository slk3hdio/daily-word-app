from flask import Flask, jsonify, request
from __init__ import op_password
from database import database

app_name = 'word'
base_url = '/' + app_name + '/api'
app = Flask(app_name)

@app.route(base_url, methods=['GET'])
def api_index():
    return jsonify({
        'status': 'ok',
        'message': 'hello!'
    })

@app.route(base_url + '/register', methods=['POST'])
def register_api():
    data = request.get_json()
    # 解析数据
    try:
        qqid = data['user_qq']
        op_password_ = data['op_password']
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
    # 验证op密码
    if op_password_ != op_password:
        return jsonify({
            'status': 'error',
            'message': 'op_password is wrong'
        })
    # 注册
    return database.register(qqid)


@app.route(base_url + '/daily_word', methods=['POST'])
def daily_word_api():
    data = request.get_json()
    # 解析数据
    try:
        user_qq = data['user_qq']
        num = data['num']
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
    # 获取单词
    words = database.get_words(num)
    # 记录日志
    database.logging_record(word_id=words[0]['id'], user=user_qq)
    

    
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'page not found'
    })