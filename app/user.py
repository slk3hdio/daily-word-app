from logger import Logger

class User:
    logger = Logger('user')
    def __init__(self, user_id=None, user_qqid=None, username=None):
        self.id = int(user_id) if user_id else None
        self.username = username
        self.qqid = int(user_qqid) if user_qqid else None

    def __eq__(self, other):
        self.logger.debug(f"user1: {self.id}: {self.id.__class__.__name__}, {self.qqid}:{self.qqid.__class__.__name__},{self.username}, user2: {other.id}: {other.id.__class__.__name__},{other.qqid}:{other.qqid.__class__.__name__},{other.username}")
        result = (self.id == other.id or self.qqid == other.qqid)
        self.logger.debug(f"result: {result}")
        return result

    def __str__(self):
        return str(self.id or self.qqid or self.username or 'unknown user')
