import mysql.connector

op_password = 'yiyisiwuyisi'
conn = mysql.connector.connect(
    host="localhost",
    user="ecs-user",
    password="Mm.123456",
    database="WORD"
)
cur = conn.cursor()

cur.execute("TRUNCATE TABLE words")
cur.execute("TRUNCATE TABLE meanings")
cur.execute("TRUNCATE TABLE tags")

with open ('words.txt', 'r') as f:
    for line in f:
        contents = line.split()
        if len(contents) == 1:
            continue
        word = contents[0]
        print(f"cur:{word}", end='   ')
        cur.execute("INSERT INTO words (word) VALUES (%s)", (word,))
        id = cur.lastrowid
        print(f"id:{id}", end='   ')
        cur.execute("INSERT INTO tags (id, tag) VALUES (%s, %s)", (id, 'CET6'))
        for meaning in contents[1:]:
            dual_part_of_speech = None
            if '&' in meaning:
                dual_part_of_speech, meaning = meaning.split('&')
            print(f"meaning:{meaning}", end='   ')
            part_of_speech, definitions = meaning.split('.')
            print(f"part_of_speech:{part_of_speech}", end='   ')
            print(f"definitions:{definitions}")
            for definition in definitions.split('；'):
                if dual_part_of_speech:
                    cur.execute("INSERT INTO meanings (id, part_of_speech, definition) VALUES (%s, %s, %s)", (id, dual_part_of_speech, definition))
                cur.execute("INSERT INTO meanings (id, part_of_speech, definition) VALUES (%s, %s, %s)", (id, part_of_speech, definition))
        conn.commit()

cur.close()
conn.close()

#menace   vt.&vi.&n.(进行)威胁
#rally   n.&vt.&vi.(重新)集合
#suicide   n.&vi.&vt.自杀
#tramp   vt.&vi.&n.步行，跋涉
#trample   vt.&vi.&n.践踏，蹂躏