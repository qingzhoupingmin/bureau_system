# -*- coding: utf-8 -*-
import pymysql

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='Oppor831t',
    database='tianjin_bureau',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute('SELECT username, role, full_name FROM users LIMIT 20')
for row in cursor.fetchall():
    print(f"{row[0]:20s} {row[1]:20s} {row[2]}")

conn.close()