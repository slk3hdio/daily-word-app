from flask import Flask, jsonify, request
from __init__ import op_password
from logger import Logger
from database import database, User
from daily_word import DailyWord
from functools import wraps

app_name = 'word'
base_url = '/' + app_name + '/api'
app = Flask(app_name)
logger = Logger('routes')


def log_addr(route_fun):
    @wraps(route_fun)
    def wrapper_fun(*args, **kwargs):
        logger.info(f'{route_fun.__name__}: received request from {request.remote_addr}')
        return route_fun(*args, **kwargs)
    return wrapper_fun


def check_op_password(route_fun):
    @wraps(route_fun)
    def wrapper_fun(*args, **kwargs):
        try:
            op_password_ = request.get_json()['op_password']
        except Exception as e:
            logger.warning(f'{route_fun.__name__}: op_password not found: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'op_password not found'
            })
        if op_password_ != op_password:
            logger.warning(f'{route_fun.__name__}: op_password is wrong')
            return jsonify({
                'status': 'error',
                'message': 'op_password is wrong'
            })
        return route_fun(*args, **kwargs)
    return wrapper_fun


def check_user_registered(route_fun):
    @wraps(route_fun)
    def wrapper_fun(*args, **kwargs):
        try:
            user_qq = request.get_json()['user_qq']
        except Exception as e:
            logger.warning(f'{route_fun.__name__}: user_qq not found: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'user_qq not found'
            })
        user = User(user_qqid=user_qq)
        if not database.get_register_info(user):
            logger.warning(f'{route_fun.__name__}: user not registered')
            return jsonify({
                'status': 'error',
                'message': 'user not registered'
            })
        return route_fun(*args, **kwargs)
    return wrapper_fun


def error_json(message):
    return jsonify({
        'status': 'error',
        'message': message
    })


@app.route(base_url, methods=['GET'])
def api_index():
    """
     测试连接
    :return:
    """
    return jsonify({
        'status': 'ok',
        'message': 'Hello!'
    })


@app.route(base_url + '/register', methods=['POST'])
@check_op_password
@log_addr
def register_api():
    """
     注册
     请求参数：
      user_qq：QQ号
      op_password：操作密码
    :return: json格式的结果
    成功：
    {
        "status": "ok",
        "message": "user registered"
    }
    失败：
    {
        "status": "error",
        "message": 错误信息
    }
    """
    data = request.get_json()
    # 解析数据
    try:
        qqid = data['user_qq']
    except Exception as e:
        logger.warning(f'register: data parse failed: {str(e)}')
        return error_json(str(e))
    # 注册
    return database.register(qqid)


@app.route(base_url + '/daily_word/create', methods=['POST'])
@check_op_password
@log_addr
def daily_word_api():
    """
     创建每日一词
     请求参数：
      user_qq：创建者的QQ号
      num：单词数量，1-10 若超过10，则默认为10，低于1，则默认为1
      is_review：是否为复习模式，为true则从已复习的单词中选择，为false则从所有单词中选择
      op_password：操作密码

    * 每日一词的创建有上限，超过上限则无法创建，且同一个用户同时只能有一个每日一词。
    :return: json格式的结果
    成功：
    {
        "status": "ok",
        "message": 列表，每项为单词的发音及释义
    }
    失败：
    {
        "status": "error",
        "message": 错误信息
    }
    """
    data = request.get_json()
    # 解析数据
    try:
        user_qq = data['user_qq']
        num = data['num']
        is_review = data['is_review']

    except Exception as e:
        logger.error(f'daily_word_api: data parse failed: {str(e)}')
        return error_json(str(e))

    # 创建每日一词
    user = User(user_qqid=user_qq)
    if not database.get_register_info(user):
        logger.warning(f'daily_word_api: user not registered')
        return error_json('user not registered')
    if DailyWord.daily_word_full():
        logger.warning(f'daily_word_api: daily word is full')
        return error_json('daily word is full')
    if DailyWord.get_daily_word(user) is not None:
        logger.warning(f'daily_word_api: the user has already created a daily word')
        return error_json('the user has already created a daily word')
    
    daily_word = DailyWord(num, user, is_review)
    return jsonify({
        'status': 'ok',
        'message': daily_word.get_dictation()
    })


@app.route(base_url + '/daily_word/dictation', methods=['POST'])
@check_user_registered
@check_op_password
@log_addr
def daily_word_dictation_api():
    """
     获取每日一词的单词提示
     请求参数：
      user_qq：创建者QQ号
      op_password：操作密码
    :return: json格式的结果
    成功：
    {
        "status": "ok",
        "message": 列表，每项为单词的发音及释义
    }
    失败：
    {
        "status": "error",
        "message": 错误信息
    }
    """
    # 解析数据
    data = request.get_json()
    try:
        user_qq = data['user_qq']
    except Exception as e:
        logger.error(f'daily_word_dictation_api: data parse failed: {str(e)}')
        return error_json(str(e))
    # 获取用户的每日一词
    daily_word = DailyWord.get_daily_word(User(user_qqid=user_qq))
    if daily_word is None:
        logger.warning(f'daily_word_dictation_api: the user has not created a daily word yet')
        return error_json('the user has not created a daily word yet')

    return jsonify({
        'status': 'ok',
        'message': daily_word.get_dictation()
    })


@app.route(base_url + '/daily_word/commit', methods=['POST'])
@check_op_password
@log_addr
def daily_word_commit_api():
    """
     提交每日一词的答案
     请求参数：
      committer_qq：提交者的QQ号
      owner_qq：每日一词的创建者的QQ号
      answer：提交的答案
      op_password：操作密码

     * 若提交的答案和单词列表中的任意一词匹配，则视为答案正确。已经答对的单词不能重复提交
    :return: json格式的结果
    成功：
    {
        "status": "ok",
        "message": "commit success"/"words all cleared"
    }
    失败：
    {
        "status": "error",
        "message": 错误信息
    }
    """
    # 解析数据
    data = request.get_json()
    try:
        committer_qq = data['committer_qq']
        owner_qq = data['owner_qq']
        answer = data['answer']
        # 检查用户是否注册
        owner = User(user_qqid=owner_qq)
        if not database.get_register_info(owner):
            logger.warning(f'daily_word_commit_api: owner not registered')
            return error_json('owner not registered')
        
        committer = User(user_qqid=committer_qq)
        if not database.get_register_info(committer):
            logger.warning(f'daily_word_commit_api: committer not registered')
            return error_json('committer not registered')
        
    except Exception as e:
        logger.error(f'daily_word_commit_api: data parse failed: {str(e)}')
        return error_json(str(e))

    # 获取每日一词
    daily_word = DailyWord.get_daily_word(owner)
    if daily_word is None:
        logger.warning(f'daily_word_commit_api: the owner has not created a daily word yet')
        return error_json('the owner has not created a daily word yet')

    # 提交答案
    status, left_num = daily_word.commit_word(answer, committer)
    if status == 'ok':
        if left_num == 0:
            message = 'words all cleared'
        else:
            message = 'commit success'
        return jsonify({
            'status': 'ok',
            'message': message
        })
    
    elif status == 'duplicate':
        logger.info(f"daily_word_commit_api: {str(committer)}'s answer is duplicate")
        return error_json('duplicate answer')

    else:
        logger.info(f"daily_word_commit_api: {str(committer)}'s answer is wrong")
        return error_json('wrong answer')
    
    
@app.route(base_url + '/daily_word/cancel', methods=['POST'])
@check_user_registered
@check_op_password
@log_addr
def daily_word_cancel_api():
    """
     取消每日一词
     请求参数：
      user_qq：每日一词的创建者的QQ号
      op_password：操作密码
    :return: json格式的结果
    成功：
    {
        "status": "ok",
        "message": "cancel success"
    }
    失败：
    {
        "status": "error",
        "message": 错误信息
    }
    """
    # 解析数据
    data = request.get_json()
    try:
        owner_qq = data['user_qq']
    except Exception as e:
        logger.error(f'daily_word_cancel_api: data parse failed: {str(e)}')
        return error_json(str(e))

    # 获取每日一词
    daily_word = DailyWord.get_daily_word(User(user_qqid=owner_qq))
    if daily_word is None:
        return error_json('the user has not created a daily word yet')

    # 取消每日一词
    daily_word.cancel()
    return jsonify({
        'status': 'ok',
        'message': 'cancel success'
    })


@app.errorhandler(404)
def page_not_found(e):
    """
     处理404错误
    """
    return jsonify({
        'status': 'error',
        'message': 'page not found'
    })