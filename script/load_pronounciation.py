import mysql.connector


op_password = 'yiyisiwuyisi'
conn = mysql.connector.connect(
    host="localhost",
    user="ecs-user",
    password="Mm.123456",
    database="WORD"
)
cur = conn.cursor()
for index in range(1, 22):
    with open('pronounciation' + str(index) + '.0.txt') as f:
        print("current file: " + 'pronounciation' + str(index) + '.0.txt')
        for line in f:
            word, pronounciation_uk, pronounciation_us = line.split()
            pronounciation_uk = pronounciation_uk[1:-1]
            pronounciation_us = pronounciation_us[1:-1]

            cur.execute("UPDATE words SET pronunciation_uk = %s, pronunciation_us = %s WHERE word = %s", (pronounciation_uk, pronounciation_us, word))
            conn.commit()

    

