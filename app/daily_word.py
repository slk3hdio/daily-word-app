from __init__.py import Logger
from database import database

class DailyWord:
    logger = Logger(__name__)
    all_daily_words = []
    max_daily_words = 1

    @classmethod
    def daily_word_full(cls):
        if len(all_daily_words) >= cls.max_daily_words:
            return True
        return False

    def __init__(self, num, user):
        self.owner = user
        if num > 10:
            num = 10
        if num < 1:
            num = 1
        self.words = get_words(num)
        self.cleared_words = []
        self.word_num = len(self.words)
        all_daily_words.append(self)
        self.logger.info(f"user {user_id} created a daily word with {self.word_num} words")

    def __del__(self, user):
        all_daily_words.remove(self)
        self.logger.info(f"user {str(user)} deleted a daily word")


    def commit_word(self, user_word, user):
        for i in range(self.word_num):
            if self.words[i].word == user_word:
                self.cleared_words.append(self.words[i])
                self.words.pop(i)
                self.logger.info(f"user {user_id} cleared a word: {user_word}")

                database.logging_record(user_id, self.words[i].id)
                return True

        self.logger.info(f"user {user_id} committed a wrong answer: {user_word}")
        return False

    def get_left_word_num(self):
        return self.word_num - len(self.cleared_words)

    def get_words(self):
        word_list = []
        for word in self.words:
            word_list.append(str(word))
        for word in self.cleared_words:
            word_list.append(str(word))
        return word_list

    def get_owner(self):
        return self.owner

