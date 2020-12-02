import sqlite3, config

connection = sqlite3.connect(config.DB_PATH)

cursor = connection.cursor()

cursor.execute(""" DROP TABLE stock_price""")

cursor.execute(""" DROP TABLE stock """)

connection.commit()