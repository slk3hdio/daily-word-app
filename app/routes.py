from flask import Flask, jsonify, request
from __init__ import op_password
from database import database, User
from daily_word import DailyWord

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


@app.route(base_url + '/daily_word/create', methods=['POST'])
def daily_word_api():
    data = request.get_json()
    # 解析数据
    try:
        user_qq = data['user_qq']
        num = data['num']
        op_password_ = data['op_password']

        if op_password_ != op_password:
            return jsonify({
                'status': 'error',
                'message': 'op_password is wrong'
            })

        user = User(user_qqid=user_qq)
        if not database.get_register_info(user):
            return jsonify({
                'status': 'error',
                'message': 'user not registered'
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

    # 创建每日一词
    if DailyWord.daily_word_full():
        return jsonify({
            'status': 'error',
            'message': 'daily word full'
        })
    daily_word = DailyWord(num, user)
    return jsonify({
        'status': 'ok',
        'message': daily_word.get_dictation()
    })

@app.route(base_url + '/daily_word/dictation', methods=['GET'])
def daily_word_dictation_api():
    # 解析数据
    data = request.get_json()
    try:
        user_qq = data['user_qq']
        op_password_ = data['op_password']

        if op_password_ != op_password:
            return jsonify({
                'status': 'error',
                'message': 'op_password is wrong'
            })
        # 检查用户是否注册
        user = User(user_qqid=user_qq)
        if not database.get_register_info(user):
            return jsonify({
                'status': 'error',
                'message': 'user not registered'
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
    # 获取用户的每日一词
    daily_word = DailyWord.get_daily_word(user)
    if daily_word is None:
        return jsonify({
            'status': 'error',
            'message': 'the user has not created a daily word yet'
        })

    return jsonify({
        'status': 'ok',
        'message': daily_word.get_dictation()
    })

@app.route(base_url + '/daily_word/commit', methods=['POST'])
def daily_word_commit_api():
    # 解析数据
    data = request.get_json()
    try:
        committer_qq = data['committer_qq']
        owner_qq = data['owner_qq']
        answer = data['answer']
        op_password_ = data['op_password']

        if op_password_ != op_password:
            return jsonify({
                'status': 'error',
                'message': 'op_password is wrong'
            })
        # 检查用户是否注册
        owner = User(user_qqid=owner_qq)
        if not database.get_register_info(owner):
            return jsonify({
                'status': 'error',
                'message': 'owner not registered'
            })
        committer = User(user_qqid=committer_qq)
        if not database.get_register_info(committer):
            return jsonify({
                'status': 'error',
                'message': 'committer not registered'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

    # 获取每日一词
    daily_word = DailyWord.get_daily_word(owner)
    if daily_word is None:
        return jsonify({
            'status': 'error',
            'message': 'the owner has not created a daily word yet'
        })

    # 提交答案
    if daily_word.commit_word(answer, committer):
        if daily_word.left_num == 0:
            daily_word.cancel()
            message = 'words all cleared'
        else:
            message = 'commit success'
        return jsonify({
            'status': 'ok',
            'message': message
        })

    else:
        return jsonify({
            'status': 'error',
            'message': 'wrong answer'
        })

@app.route(base_url + '/daily_word/cancel', methods=['POST'])
def daily_word_cancel_api():
    # 解析数据
    data = request.get_json()
    try:
        owner_qq = data['owner_qq']
        op_password_ = data['op_password']

        if op_password_ != op_password:
            return jsonify({
                'status': 'error',
                'message': 'op_password is wrong'
            })
        # 检查用户是否注册
        owner = User(user_qqid=owner_qq)
        if not database.get_register_info(owner):
            return jsonify({
                'status': 'error',
                'message': 'owner not registered'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

    # 获取每日一词
    daily_word = DailyWord.get_daily_word(owner)
    if daily_word is None:
        return jsonify({
            'status': 'error',
            'message': 'the owner has not created a daily word yet'
        })

    # 取消每日一词
    daily_word.cancel()
    return jsonify({
        'status': 'ok',
        'message': 'cancel success'
    })



    
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'page not found'
    })