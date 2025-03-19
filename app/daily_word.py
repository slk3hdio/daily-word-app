from database import database
from logger import Logger
from word import Word
from user import User


class DailyWord:
    logger = Logger(__name__)
    all_daily_words = []
    max_daily_words = 100

    @classmethod
    def daily_word_full(cls):
        if len(cls.all_daily_words) >= cls.max_daily_words:
            return True
        return False

    @classmethod
    def daily_word_num(cls):
        return len(cls.all_daily_words)

    @classmethod
    def cancel_daily_word(cls, user):
        for daily_word in cls.all_daily_words:
            if daily_word.owner == user:
                cls.all_daily_words.remove(daily_word)
                cls.logger.info(f"user {str(user)} canceled his/her daily word")
                return True
        cls.logger.info(f"user {str(user)} tried to cancel a daily word but it doesn't exist")
        return False
    
    @classmethod
    def delete_daily_word(cls, daily_word):
        cls.logger.info(f"user {str(daily_word.owner)}'s daily word was deleted")
        cls.all_daily_words.remove(daily_word)

    @classmethod
    def get_daily_word(cls, user):
        for daily_word in cls.all_daily_words:
            if daily_word.owner == user:
                return daily_word
        return None


    def __init__(self, num, user:User, review=False):
        self.owner = user
        if num > 10:
            num = 10
        if num < 1:
            num = 1
        self.words = database.get_words(num, (user if review else None))
        self.cleared_words = []
        self.word_num = len(self.words)
        self.all_daily_words.append(self)
        self.logger.info(f"user {str(user)} created a daily word with {self.word_num} words, review={review}")

    def cancel(self):
        self.all_daily_words.remove(self)
        self.logger.info(f"user {str(self.owner)} canceled his/her daily word")

    def get_dictation(self):
        s = []
        for i in range(self.word_num):
            s.append(f"{i+1}. {self.words[i].get_dictation()}")
        return s

    def commit_word(self, user_word, user):
        for i in range(len(self.words)):
            if str(self.words[i].word) == user_word:
                self.cleared_words.append(self.words[i])
                database.logging_record(self.words[i].id, user)
                self.words.pop(i)
                self.logger.info(f"user {str(user)} committed a correct answer: {user_word} to {str(self.owner)}'s daily word")
                left_num = self.get_left_num()
                
                if left_num == 0:
                    self.logger.info(f"user {str(self.owner)}'s daily word is cleared")
                    self.all_daily_words.remove(self)
                
                return 'ok', left_num
            
        for j in range(len(self.cleared_words)):
            if str(self.cleared_words[j].word) == user_word:
                self.logger.info(f"user {str(user)} tried to commit a word that has already been cleared")
                return 'duplicate', self.get_left_num()

        self.logger.info(f"user {str(user)} committed a wrong answer: {user_word} to {str(self.owner)}'s daily word")
        return 'wrong', self.get_left_num()

    def get_left_num(self):
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

