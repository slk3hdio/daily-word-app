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

    def __str__(self):
        s = f'{word} [英]/{pronunciation_us}/ [美]/{pronunciation_uk}/ '
        for meaning in meanings:
            s += f'<{meaning[0]}>.{meaning[1]}; '
        return s

    # def __eq__(self, other):
    #     return self.word == other

class User:
    def __init__(self, user_id=None, user_qqid=None):
        self.qqid = user_qqid
        self.id = user_id

    def __str__(self):
        return str(self.id or self.qqid or 'unknown user')

    
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
            Logger.logger.info('auth_system connected')

            self.conn_word = mysql.connector.connect(
                host="localhost",
                user="ecs-user",
                password="Mm.123456",
                database="WORD"
            )
            Logger.logger.info('WORD connected')
        except Exception as e:
            Logger.logger.critical(str(e))
            raise

    def check_if_registered(self, user):
        try:
            cur = self.conn_auth.cursor()
            if user.id:
                cur.execute("SELECT * FROM users WHERE id= %s", (user.id,))
            elif user.qqid:
                cur.execute("SELECT * FROM users WHERE qqid= %s", (user.qqid,))
            else:
                return False
            cur.close()
            if cur.fetchone():
                return True
            else:
                return False
        except Exception as e:
            Logger.logger.error(f'failed to check if user {str(user)} is registered due to [{str(e)}] when checking register')
            cur.close()
            return False

    def get_user_id(self, qqid):
        try:
            cur = self.conn_auth.cursor()
            cur.execute("SELECT id FROM users WHERE qqid= %s", (qqid,))
            user_id = cur.fetchone()
            if user_id:
                return user_id[0]
            else:
                return None
        except Exception as e:
            Logger.logger.error(f'failed to get user id for {qqid} due to [{str(e)}] when getting user id')
            return None
        finally:
            cur.close()


    def register(self, qqid):
        Logger.logger.info(f'{qqid} registering')
        # 验证qq号是否已注册
        if self.check_if_registered(qqid=qqid):
            Logger.logger.warning(f'{qqid} register failed because user already exists')
            return jsonify({
                'status': 'error',
                'message': 'user already exists'
            })
        # 注册用户
        try:
            cur.execute("INSERT INTO users (username, qqid) VALUES (%s, %s)", (qqid, qqid))
            self.conn_auth.commit()
            Logger.logger.info(f'{qqid} registered')
            return jsonify({
                'status': 'ok',
                'message': 'user registered'
            })
        except Exception as e:
            Logger.logger.error(f'{qqid} register failed due to [{str(e)}] when registering')
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
        finally:
            cur.close()

    def get_words(self, num):
        # 获取单词数量
        try:
            Logger.logger.info(f'getting {num} words')
            cur = self.conn_word.cursor()
            cur.execute("SELECT COUNT(*) FROM words")
            count = cur.fetchone()[0]
        except Exception as e:
            Logger.logger.error(f'failed to get words due to [{str(e)}] when counting words')
            return []

        # 随机获取单词
        words = []
        for i in range(30):
            if len(words) >= num:
                break
            word_id = random.randint(1, count)
            try:
                cur.execute("SELECT * FROM words WHERE id= %s", (id,))
                word = Word(*cur.fetchone())
                cur.execute("SELECT * FROM meanings WHERE word_id= %s", (id,))
                for meaning in cur.fetchall():
                    word_id, part_of_speech, definition = meaning
                    word.add_meaning(part_of_speech, definition)
                words.append(word)
            except Exception as e:
                if i == 29:
                    Logger.logger.error(f'failed to get word {word_id} due to [{str(e)}] when getting word')
                    return []
                Logger.logger.warning(f'failed to get word {word_id} due to [{str(e)}], retrying')
                continue

        cur.close() 
        Logger.logger.info(f'got words: {words}')
        return words


    def logging_record(self, word_id, user):
        '''
        记录用户的单词学习记录
        :param word_id: 单词id
        :param user: 用户对象
        :return: 返回json格式的响应
        '''
        if not self.check_if_registered(user):
            return jsonify({
                'status': 'error',
                'message': 'user not registered'
            })
        try:
            cur = self.conn_word.cursor()
            cur.execute("INSERT INTO user_records (user_id, word_id, count) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE count=count+1", (user_id, word_id))
            self.conn_word.commit()
            Logger.logger.info(f'user {user_id} logged record for word {word_id}')
            return jsonify({
                'status': 'ok',
                'message': 'logged record'
            })
        except Exception as e:
            Logger.logger.error(f'failed to log record for user {user_id} due to [{str(e)}] when logging')
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
        finally:
            cur.close()

database = Database()
            



