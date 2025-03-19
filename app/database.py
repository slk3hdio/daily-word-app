import mysql.connector
from logger import Logger
from flask import jsonify
from word import Word
from user import User



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
                self.logger.info(f'get register info for {str(user)}: success')
                user.id = result[0]
                user.username = result[1]
                user.qqid = result[2]
                return True
            else:
                self.logger.info(f'get register info for {str(user)}: failed')
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

    def get_words(self, num, user:User=None):
        """
        获取指定数量的单词    
        :param num: 单词数量
        :param user: 用户对象，如果非空，则从用户的学习记录中获取单词，否则从所有单词中获取
        :return: 单词列表
        """
        # 随机获取单词
        words = []
        cur = None
        try:
            cur = self.conn_word.cursor()  
            if user is not None:
                self.logger.info(f'getting {num} words from user {str(user)}\'s record')
                cur.execute("SELECT u.id, w.word, w.pronunciation_uk, w.pronunciation_us, m.part_of_speech, m.definition FROM (SELECT * FROM user_record as r WHERE r.user_id=%s ORDER BY r.count LIMIT %s) as u NATURAL JOIN words as w NATURAL JOIN meanings as m", (user.id, num))  
            else: 
                self.logger.info(f'getting {num} words from word table')             
                cur.execute("SELECT w.id, word, pronunciation_uk, pronunciation_us, part_of_speech, definition FROM (SELECT * FROM words ORDER BY RAND() LIMIT %s) AS w, meanings AS m where w.id=m.id", (num,))
            word=None
            result = cur.fetchall()
            for row in result:
                self.logger.debug(str(row))
                if word and word.id == row[0]:
                    word.add_meaning(row[4], row[5])
                else:
                    if word:
                        words.append(word)
                    word = Word(row[0], row[1], row[2], row[3])
            if word:
                words.append(word)
        except Exception as e:
            self.logger.error(f'failed to get words due to [{str(e)}] when getting words')
        finally:
            if cur:
                cur.close()    
        if not words:
            self.logger.error(f'no word matching condition found')              
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
            cur.execute("INSERT INTO user_record (user_id, id, count) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE count=count+1", (str(user), word_id))
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
            



