import mysql.connector
from openai import OpenAI

op_password = 'yiyisiwuyisi'
conn = mysql.connector.connect(
    host="localhost",
    user="ecs-user",
    password="Mm.123456",
    database="WORD"
)
cur = conn.cursor()


client = OpenAI(api_key = '3b144066-c88f-4796-b19e-1fa3cc71253b', base_url = 'https://ark.cn-beijing.volces.com/api/v3')


cur.execute("SELECT * FROM words where id > 2000")
count = 0
words = ''
prompt = ''
file_content = ''
for row in cur.fetchall():
    count += 1
    id, word = row[0], row[1]
    words += word + '\n'
    if count % 20 == 0:
        prompt = '给出以下单词的音标：\n' + words + \
            '你的回答应该是格式化的，每行一个单词以及其英式发音和美式发音，用空格隔开。\n' + \
            '示例：abbreviation /əˌbriːviˈeɪʃ(ə)n/ /əˌbriːviˈeɪʃən/\n' + \
            '除此之外，不要输出其他内容' 

        response = client.chat.completions.create(
            model = 'deepseek-v3-241226',
            messages = [
                {'role':'system', 'content': '你是人工智能助手'},
                {'role': 'user', 'content': prompt}
            ],
            stream = False
        )
        file_content += response.choices[0].message.content + '\n'
        words = ''
        prompt = ''

        if count % 100 == 0:
            with open('pronounciation' + str(count / 100) + '.txt', 'w', encoding='utf-8') as f:
                f.write(file_content)
            file_content = ''
    


if words:
    prompt = '给出以下单词的音标：\n' + words + \
            '你的回答应该是格式化的，每行一个单词以及其英式发音和美式发音，用空格隔开。\n' + \
            '示例：abbreviation /əˌbriːviˈeɪʃ(ə)n/ /əˌbriːviˈeɪʃən/\n' + \
            '除此之外，不要输出其他内容' 
    response = client.chat.completions.create(
            model = 'deepseek-v3-241226',
            messages = [
                {'role':'system', 'content': '你是人工智能助手'},
                {'role': 'user', 'content': prompt}
            ],
            stream = False
        )
    file_content += response.choices[0].message.content + '\n'
    with open('pronounciation.txt', 'w', encoding='utf-8') as f:
        f.write(file_content)