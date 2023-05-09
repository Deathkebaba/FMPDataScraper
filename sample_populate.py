import sqlite3
import core

# tickers you want in your repository
tickers = ["AAPL", "TSLA", "MSFT", "COST", "AMZN", "META"]


conn = sqlite3.connect(core.db_name)
for ticker in tickers:
    core.db_update_stock(conn, ticker)
conn.commit()
conn.close()
