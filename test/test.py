import bcrypt
import mysql.connector

# password = b'password'
# salt = bcrypt.gensalt()
# hashed_password = bcrypt.hashpw(password, salt)

# print(hashed_password)

# while True:
#     password = input("Enter password: ")
#     if password == "exit":
#         break
#     if bcrypt.hashpw(password.encode('utf-8'), salt) == hashed_password:
#         print("Access granted")
#     else:
#         print("Access denied")


# op_password = 'yiyisiwuyisi'
# conn = mysql.connector.connect(
#     host="localhost",
#     user="ecs-user",
#     password="Mm.123456",
#     database="WORD"
# )

# cur = conn.cursor()
# cur.execute("SELECT * FROM words")
# for row in cur:
#     print(row)

# str = '你好'
# print(len(str))
# for char in str:
#     print(char)

# class User:
#     def __init__(self, user_id=None, user_qqid=None, username=None):
#         self.id = user_id
#         self.username = username
#         self.qqid = user_qqid

#     def __eq__(self, other):
#         return self.id == other.id or self.qqid == other.qqid or self.username == other.username

#     def __str__(self):
#         return str(self.id or self.qqid or self.username or 'unknown user')
    
a = False or True or False
print(a)