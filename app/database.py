import mysql.connector
import random
from __init__ import Logger
from flask import jsonify

class Word:
    def __init__(self, word_id, word, pronunciation_uk, pronunciation_us):
        self.id = word_id
        self.word = word
        self.pronunciation_uk = pronunciation_uk
        self.pronunciation_us = pronunciation_us
        self.meanings = []

    def add_meaning(self, part_of_speech, definition):
        self.meanings.append((part_of_speech, definition))

    def get_dictation(self):
        s = f'[英]/{self.pronunciation_us}/ [美]/{self.pronunciation_uk}/ '
        for meaning in self.meanings:
            s += f'<{meaning[0]}>.{meaning[1]}; '
        return s

    def __str__(self):
        s = f'{self.word} [英]/{self.pronunciation_us}/ [美]/{self.pronunciation_uk}/ '
        for meaning in self.meanings:
            s += f'<{meaning[0]}>.{meaning[1]}; '
        return s

    # def __eq__(self, other):
    #     return self.word == other

class User:
    def __init__(self, user_id=None, user_qqid=None, username=None):
        self.id = user_id
        self.username = username
        self.qqid = user_qqid

    def __eq__(self, other):
        return self.id == other.id or self.qqid == other.qqid or self.username == other.username

    def __str__(self):
        return str(self.id or self.qqid or self.username or 'unknown user')

    
class Database:
    logger = Logger('database')

    def __init__(self):
        try:
            self.conn_auth = mysql.connector.connect(
                host="localhost",
                user="ecs-user",
                password="Mm.123456",
                database="auth_system"
            )
            self.logger.info('auth_system connected')

            self.conn_word = mysql.connector.connect(
                host="localhost",
                user="ecs-user",
                password="Mm.123456",
                database="WORD"
            )
            self.logger.info('WORD connected')
        except Exception as e:
            self.logger.critical(str(e))
            raise

    def get_register_info(self, user):
        """
        获取用户注册信息
        :param user: 用户对象，id和qqid不能同时为空
        :return: 如果用户已注册，返回True，并且补全用户信息；否则返回False
        """
        cur = None
        try:
            cur = self.conn_auth.cursor()

            if user.id:
                cur.execute("SELECT id, username, qqid FROM users WHERE id= %s", (user.id,))
            elif user.qqid:
                cur.execute("SELECT id, username, qqid FROM users WHERE qqid= %s", (user.qqid,))
            else:
                raise ValueError('user id or qqid not provided')

            result = cur.fetchone()
            cur.close()
            if result:
                user.id = result[0]
                user.username = result[1]
                user.qqid = result[2]
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'failed to get register info for {str(user)} due to [{str(e)}] when getting register info')
            if cur:
                cur.close()
            return False

    def register(self, qqid):
        self.logger.info(f'{qqid} registering')
        # 验证qq号是否已注册
        user = User(user_qqid=qqid)
        if self.get_register_info(user):
            self.logger.info(f'{qqid} register failed due to user already registered')
            return jsonify({
                'status': 'error',
                'message': 'user already registered'
            })
        # 注册用户
        cur = None
        try:
            cur = self.conn_auth.cursor()
            cur.execute("INSERT INTO users (username, qqid) VALUES (%s, %s)", (qqid, qqid))
            self.conn_auth.commit()
            self.logger.info(f'{qqid} registered')
            return jsonify({
                'status': 'ok',
                'message': 'user registered'
            })
        except Exception as e:
            self.logger.error(f'{qqid} register failed due to [{str(e)}] when registering')
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
        finally:
            cur.close()

    def get_words(self, num):
        # 获取单词数量
        try:
            self.logger.info(f'getting {num} words')
            cur = self.conn_word.cursor()
            cur.execute("SELECT COUNT(*) FROM words")
            count = cur.fetchone()[0]
        except Exception as e:
            self.logger.error(f'failed to get words due to [{str(e)}] when counting words')
            return []

        # 随机获取单词
        words = []
        for i in range(30):
            if len(words) >= num:
                break
            word_id = random.randint(1, count)
            try:
                cur.execute("SELECT * FROM words WHERE id= %s", (word_id,))
                word = Word(*cur.fetchone())
                cur.execute("SELECT * FROM meanings WHERE id= %s", (word_id,))
                for meaning in cur.fetchall():
                    word_id, part_of_speech, definition = meaning
                    word.add_meaning(part_of_speech, definition)
                words.append(word)
            except Exception as e:
                if i == 29:
                    self.logger.error(f'failed to get word {word_id} due to [{str(e)}] when getting word')
                    return []
                self.logger.warning(f'failed to get word {word_id} due to [{str(e)}], retrying')
                continue

        cur.close() 
        self.logger.info(f'got words: {[str(word) for word in words]}')
        return words

    def logging_record(self, word_id, user:User):
        """
        记录用户的单词学习记录
        :param word_id: 单词id
        :param user: 用户对象
        :return: 返回json格式的响应
        """
        if not self.get_register_info(user):
            return jsonify({
                'status': 'error',
                'message': 'user not registered'
            })
        cur = None
        try:
            cur = self.conn_word.cursor()
            cur.execute("INSERT INTO user_records (user_id, word_id, count) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE count=count+1", (str(user), word_id))
            self.conn_word.commit()
            self.logger.info(f'user {str(user)} logged record for word {word_id}')
            return jsonify({
                'status': 'ok',
                'message': 'logged record'
            })
        except Exception as e:
            self.logger.error(f'failed to log record for user {str(user)} due to [{str(e)}] when logging')
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
        finally:
            cur.close()


database = Database()
            



