import aiohttp
import ujson
import sqlite3
import asyncio
import pandas as pd
from tqdm import tqdm
import orjson
from datetime import datetime, timedelta
from GetStartEndDate import GetStartEndDate
from collections import defaultdict
import re
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('FMP_API_KEY')

with open(f"json/stock-screener/data.json", 'rb') as file:
    stock_screener_data = orjson.loads(file.read())

def format_filename(industry_name):
    # Replace spaces and slashes with hyphens
    formatted_name = industry_name.replace(' ', '-').replace('/', '-')
    # Replace "&" with "and"
    formatted_name = formatted_name.replace('&', 'and')
    # Remove any extra hyphens (e.g., from consecutive spaces)
    formatted_name = re.sub(r'-+', '-', formatted_name)
    # Convert to lowercase for consistency
    formatted_name = formatted_name.lower()
    return formatted_name


date, _ = GetStartEndDate().run()
date = date.strftime('%Y-%m-%d')

def save_as_json(data, filename):
    with open(f"json/industry/{filename}.json", 'w') as file:
        ujson.dump(data, file)

def remove_duplicates(data, key):
    seen = set()
    new_data = []
    for item in data:
        if item[key] not in seen:
            seen.add(item[key])
            new_data.append(item)
    return new_data

async def historical_pe_ratio(session, class_type='sector'):
    # List to store the data
    historical_data = []
    
    # Starting point: today minus 180 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Iterate through each day
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Only fetch data for weekdays (Monday to Friday)
            date_str = current_date.strftime('%Y-%m-%d')
            data = await get_data(session, date_str, class_type)
            if data:
                historical_data+=data
        
        # Move to the next day
        current_date += timedelta(days=1)

    return historical_data

# Function to fetch data from the API
async def get_data(session, date, class_type='sector'):
    if class_type == 'sector':
        url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?date={date}&exchange=NYSE&apikey={api_key}"
    else:
        url = f"https://financialmodelingprep.com/api/v4/industry_price_earning_ratio?date={date}&exchange=NYSE&apikey={api_key}"
    async with session.get(url) as response:
        data = await response.json()
        return data

def get_each_industry_data():
    industry_data = defaultdict(list)  # Dictionary to store industries and their corresponding stock data
    for stock in stock_screener_data:
        industry = stock.get('industry')
        if industry:  # Make sure the stock has an industry defined
            # Extract relevant fields
            stock_data = {
                'symbol': stock.get('symbol'),
                'name': stock.get('name'),
                'price': stock.get('price'),
                'changesPercentage': stock.get('changesPercentage'),
                'marketCap': stock.get('marketCap'),
                'revenue': stock.get('revenue'),
            }
            # Append stock data to the corresponding industry list
            industry_data[industry].append(stock_data)

    return dict(industry_data) 

async def run():

    async with aiohttp.ClientSession() as session:
        historical_pe_list = await historical_pe_ratio(session, class_type = 'industry')


        full_industry_list = get_each_industry_data()
        for industry, stocks in full_industry_list.items():
            filename = 'industries/'+format_filename(industry)
            stocks = [item for item in stocks if item.get('marketCap') is not None and item['marketCap'] > 0]
            stocks = sorted(stocks, key=lambda x: x['marketCap'], reverse=True)
            for rank, item in enumerate(stocks, 1):
                item['rank'] = rank
            history_list = []
            for item in historical_pe_list:
                try:
                    if item['industry'] == industry:
                        history_list.append({'date': item['date'], 'pe': round(float(item['pe']),2)})
                except:
                    pass
            history_list = sorted(history_list, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=False)
            history_list = remove_duplicates(history_list, 'date')
            res = {'name': industry, 'stocks': stocks, 'history': history_list}
            save_as_json(res, filename)







    # Initialize a dictionary to store stock count, market cap, and other totals for each industry
    sector_industry_data = defaultdict(lambda: defaultdict(lambda: {
        'numStocks': 0, 
        'totalMarketCap': 0.0, 
        'totalDividendYield': 0.0, 
        'totalNetIncome': 0.0,
        'totalRevenue': 0.0,
        'totalChange1D': 0.0, 
        'totalChange1Y': 0.0,
        'peCount': 0, 
        'dividendCount': 0, 
        'change1DCount': 0, 
        'change1YCount': 0
    }))

    # Iterate through stock_screener_data to accumulate values
    for stock in stock_screener_data:
        try:
            symbol = stock.get('symbol')
            sector = stock.get('sector')
            industry = stock.get('industry')
            market_cap = stock.get('marketCap')
            dividend_yield = stock.get('dividendYield')
            net_income = stock.get('netIncome')
            revenue = stock.get('revenue')
            with open(f"json/quote/{symbol}.json","r") as file:
                quote_data = ujson.load(file)
            change_1_day = quote_data.get('changesPercentage',None)
            change_1_year = stock.get('change1Y')
            
            # Ensure both sector and industry are valid and that market cap is a valid number
            if sector and industry and market_cap is not None:
                # Update stock count and accumulate market cap
                sector_industry_data[sector][industry]['numStocks'] += 1
                sector_industry_data[sector][industry]['totalMarketCap'] += float(market_cap)
                
                # Accumulate dividend yield if available
                if dividend_yield is not None:
                    sector_industry_data[sector][industry]['totalDividendYield'] += float(dividend_yield)
                    sector_industry_data[sector][industry]['dividendCount'] += 1
                
                # Accumulate net income and revenue for profit margin calculation
                if net_income is not None and revenue is not None:
                    sector_industry_data[sector][industry]['totalNetIncome'] += float(net_income)
                    sector_industry_data[sector][industry]['totalRevenue'] += float(revenue)
                
                # Accumulate 1-month change if available
                if change_1_day is not None:
                    sector_industry_data[sector][industry]['totalChange1D'] += float(change_1_day)
                    sector_industry_data[sector][industry]['change1DCount'] += 1
                
                # Accumulate 1-year change if available
                if change_1_year is not None:
                    sector_industry_data[sector][industry]['totalChange1Y'] += float(change_1_year)
                    sector_industry_data[sector][industry]['change1YCount'] += 1
        except Exception as e:
            print(e)

    # Prepare the final data in the requested format
    overview = {}

    for sector, industries in sector_industry_data.items():
        try:
            # Sort industries by stock count in descending order
            sorted_industries = sorted(industries.items(), key=lambda x: x[1]['numStocks'], reverse=True)
            
            # Add sorted industries with averages to the overview for each sector
            overview[sector] = [
                {
                    'industry': industry,
                    'numStocks': data['numStocks'],
                    'totalMarketCap': data['totalMarketCap'],
                    'avgDividendYield': round((data['totalDividendYield'] / data['dividendCount']),2) if data['dividendCount'] > 0 else None,
                    'profitMargin': round((data['totalNetIncome'] / data['totalRevenue'])*100,2) if data['totalRevenue'] > 0 else None,
                    'avgChange1D': round((data['totalChange1D'] / data['change1DCount']),2) if data['change1DCount'] > 0 else None,
                    'avgChange1Y': round((data['totalChange1Y'] / data['change1YCount']),2) if data['change1YCount'] > 0 else None
                } for industry, data in sorted_industries
            ]
        except:
            pass

    # Assign the P/E values from pe_industry to the overview
    async with aiohttp.ClientSession() as session:
        pe_industry = await get_data(session, date, class_type='industry')
    for sector, industries in overview.items():
        for industry_data in industries:
            industry_name = industry_data['industry']

            # Look for a matching industry in pe_industry to assign the P/E ratio
            matching_pe = next((item['pe'] for item in pe_industry if item['industry'] == industry_name), None)
            
            if matching_pe is not None:
                industry_data['pe'] = round(float(matching_pe), 2)

    save_as_json(overview, filename = 'overview')
    
    industry_overview = []

    for key in overview:
        industry_overview.extend(overview[key])

    industry_overview = sorted(industry_overview, key= lambda x: x['numStocks'], reverse=True)
    
    save_as_json(industry_overview, filename='industry-overview')


    sector_overview = []

    for sector, industries in sector_industry_data.items():
        total_market_cap = 0
        total_stocks = 0
        total_dividend_yield = 0
        total_net_income = 0
        total_revenue = 0
        total_change_1d = 0
        total_change_1y = 0

        dividend_count = 0
        change_1d_count = 0
        change_1y_count = 0

        for industry, data in industries.items():
            # Sum up values across industries for the sector summary
            total_market_cap += data['totalMarketCap']
            total_stocks += data['numStocks']
            total_net_income += data['totalNetIncome']
            total_revenue += data['totalRevenue']
            total_change_1d += data['totalChange1D']
            total_change_1y += data['totalChange1Y']

            dividend_count += data['dividendCount']
            change_1d_count += data['change1DCount']
            change_1y_count += data['change1YCount']
            total_dividend_yield += data['totalDividendYield']

        # Calculate averages and profit margin for the sector
        sector_overview.append({
            'sector': sector,
            'numStocks': total_stocks,
            'totalMarketCap': total_market_cap,
            'avgDividendYield': round((total_dividend_yield / dividend_count), 2) if dividend_count > 0 else None,
            'profitMargin': round((total_net_income / total_revenue) * 100, 2) if total_revenue > 0 else None,
            'avgChange1D': round((total_change_1d / change_1d_count), 2) if change_1d_count > 0 else None,
            'avgChange1Y': round((total_change_1y / change_1y_count), 2) if change_1y_count > 0 else None
        })


    # Assign the P/E values from pe_industry to the overview
    async with aiohttp.ClientSession() as session:
        pe_sector = await get_data(session, date, class_type='sector')
    # Loop through sector_overview to update P/E ratios from pe_sector
    for sector_data in sector_overview:
        sector_name = sector_data['sector']

        # Find the matching sector in pe_sector and assign the P/E ratio
        matching_pe = next((item['pe'] for item in pe_sector if item['sector'] == sector_name), None)

        if matching_pe is not None:
            sector_data['pe'] = round(float(matching_pe), 2)
    sector_overview = sorted(sector_overview, key= lambda x: x['numStocks'], reverse=True)
    
    save_as_json(sector_overview, filename='sector-overview')

loop = asyncio.get_event_loop()
sector_results = loop.run_until_complete(run())