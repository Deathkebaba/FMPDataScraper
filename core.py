#get data from website
import json
from urllib.request import urlopen
import pandas as pd
import sqlite3


#YOU NEED TO ADD YOUR API KEY FOR THIS TO WORK
API_Key = "INSERT YOUR API KEY HERE"
db_name = "stock_price_data.db"

def get_jsonparsed_data(url:str)->list:
    """Parses the JSON response of FMP into a list of dictionaries

    Args:
        url: link to the FMP API

    Returns:
        list: List of dictionaries, content depends on the url given
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def downloadStockMinuteData(ticker:str)-> pd.DataFrame:
    """Gets the newest minute data for a ticker as a pandas.Dataframe. Adds a column with the ticker, which is later needed for the database.

    Args:
        ticker (str): the ticker of a stock. Example: "AAPL"
    """
    url = (f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{ticker}?apikey={API_Key}")
    data = pd.DataFrame(get_jsonparsed_data(url))
    data = data.reindex(index=data.index[::-1])
    data["date"] = pd.to_datetime(data["date"])
    data["ticker"]=ticker
    return data 

def db_initiate(conn:sqlite3.Connection)->None:
    """Creates the databases core tables.
    """
    conn.execute("CREATE TABLE tickers (ticker varchar PRIMARY KEY)")
    conn.execute("""CREATE TABLE price_data
        (date DATETIME,
        open FLOAT,
        low FLOAT,
        high FLOAT,
        close FLOAT,
        volume FLOAT,
        ticker VARCHAR,
        FOREIGN KEY(ticker) REFERENCES tickers(ticker))""")

def db_update_stock(conn:sqlite3.Connection, ticker:str)->None:
    """Gets the newest minute data for a stock and adds it to the database

    Args:
        conn (sqlite3.Connection): connection to your database
        ticker (str): the ticker of a stock. Example: "AAPL"
    """
    conn.execute(f"INSERT OR IGNORE INTO tickers (ticker) VALUES ('{ticker}')")
    result = conn.execute(f"SELECT MAX(date) FROM price_data WHERE ticker = '{ticker}'").fetchall()[0][0]
    #print(result)

    data = downloadStockMinuteData(ticker)
    if result == None:
        data.to_sql('price_data',conn, if_exists='append',index=False)
    else:
        data = data[data["date"]>result]
        data.to_sql('price_data',conn, if_exists='append',index=False)

def db_update_all(conn:sqlite3.Connection)->None:
    """Gets the newest minute data for all tickers already in the database ands adds it.

    Args:
        conn (sqlite3.Connection): connection to your database
    """
    result = conn.execute(f"SELECT ticker FROM tickers").fetchall()
    for ticker in result:
        db_update_stock(conn,ticker[0])    