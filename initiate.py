import core
import sqlite3

conn = sqlite3.connect(core.db_name)
core.db_initiate(conn)
conn.commit()
conn.close()
