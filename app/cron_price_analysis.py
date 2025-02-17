import ujson
import asyncio
import aiohttp
import sqlite3
from datetime import datetime
from ml_models.prophet_model import PricePredictor
import yfinance as yf
import pandas as pd
from tqdm import tqdm
import concurrent.futures


def convert_symbols(symbol_list):
    converted_symbols = []
    for symbol in symbol_list:
        # Determine the base and quote currencies
        base_currency = symbol[:-3]
        quote_currency = symbol[-3:]
        
        # Construct the new symbol in the desired format
        new_symbol = f"{base_currency}-{quote_currency}"
        converted_symbols.append(new_symbol)
    
    return converted_symbols

async def save_json(symbol, data):
    with open(f"json/price-analysis/{symbol}.json", 'w') as file:
        ujson.dump(data, file)

async def download_data(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        df = df.reset_index()
        df = df[['Date', 'Adj Close']]
        df = df.rename(columns={"Date": "ds", "Adj Close": "y"})
        if len(df) > 252*2: #At least 2 years of history is necessary
            q_high= df["y"].quantile(0.99)
            q_low = df["y"].quantile(0.05)
            df = df[(df["y"] > q_low)]
            df = df[(df["y"] < q_high)]
            #df['y'] = df['y'].rolling(window=10).mean()
            #df = df.dropna()
            return df
    except Exception as e:
        print(e)

async def process_symbol(ticker, start_date, end_date):
    try:
        df = await download_data(ticker, start_date, end_date)
        data = PricePredictor().run(df)
        await save_json(ticker, data)
    
    except Exception as e:
        print(e)


async def run():
    con = sqlite3.connect('stocks.db')
    
    cursor = con.cursor()
    cursor.execute("PRAGMA journal_mode = wal")
    cursor.execute("SELECT DISTINCT symbol FROM stocks WHERE marketCap > 1E9")
    stock_symbols = [row[0] for row in cursor.fetchall()]
    con.close()

    total_symbols = stock_symbols
    print(f"Total tickers: {len(total_symbols)}")
    start_date = datetime(2015, 1, 1).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")

    chunk_size = len(total_symbols) // 70  # Divide the list into N chunks
    chunks = [total_symbols[i:i + chunk_size] for i in range(0, len(total_symbols), chunk_size)]
    for chunk in chunks:
        tasks = []
        for ticker in tqdm(chunk):
            tasks.append(process_symbol(ticker, start_date, end_date))

        await asyncio.gather(*tasks)

try:
    asyncio.run(run())
except Exception as e:
    print(e)
