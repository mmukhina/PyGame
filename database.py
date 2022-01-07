import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()
result = cur.execute("""SELECT * FROM constants""").fetchall()
for i in result:
    print(i)
con.close()
