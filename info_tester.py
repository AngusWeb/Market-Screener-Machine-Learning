import yfinance as yf
import json
from datetime import datetime, timedelta
import pandas as pd
import os

def save_to_json(data, filename, ticker):
    folder_name = "rr_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    file_path = os.path.join(folder_name, filename)
    
    if isinstance(data, pd.DataFrame):
        data_dict = data.to_dict(orient='split')
        data_dict['ticker'] = ticker
    elif isinstance(data, pd.Series):
        if data.index.is_unique:
            data_dict = data.to_dict()
        else:
            data_dict = data.reset_index().to_dict(orient='records')
        data_dict = {'data': data_dict, 'ticker': ticker}
    else:
        data_dict = {'data': data, 'ticker': ticker}
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
        existing_data.append(data_dict)
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=4, default=str)
    else:
        with open(file_path, 'w') as f:
            json.dump([data_dict], f, indent=4, default=str)
    
    print(f"Data for {ticker} saved to {file_path}")

def get_comprehensive_stock_data(tickers):
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        
        # Get all stock info
        #save_to_json(stock.info, "stock_info.json", ticker)
        
        # Get historical market data (2 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=31)
        #hist = stock.history(start=start_date, end=end_date)
        #save_to_json(hist, "historical_data.json", ticker)
        
        #print(stock.calendar)
        print(stock.insider_transactions)
        # Get history metadata
        save_to_json(stock.history_metadata, "history_metadata.json", ticker)

        # Get share count
        shares = stock.get_shares_full(start=start_date.strftime("%Y-%m-%d"), end=None)
        save_to_json(shares, "shares.json", ticker)
        
        # Get financials
        save_to_json(stock.calendar, "calendar.json", ticker)
        save_to_json(stock.sec_filings, "sec_filings.json", ticker)
        
        # Income statement
        save_to_json(stock.income_stmt, "income_stmt.json", ticker)
        
        
        save_to_json(stock.quarterly_income_stmt, "quarterly_income_stmt.json", ticker)
        
        # Balance sheet
        save_to_json(stock.balance_sheet, "balance_sheet.json", ticker)
        save_to_json(stock.quarterly_balance_sheet, "quarterly_balance_sheet.json", ticker)
        
        # Cash flow statement
        save_to_json(stock.cashflow, "cashflow.json", ticker)
        save_to_json(stock.quarterly_cashflow, "quarterly_cashflow.json", ticker)
        
        # Get holders
        save_to_json(stock.major_holders, "major_holders.json", ticker)
        save_to_json(stock.institutional_holders, "institutional_holders.json", ticker)
        save_to_json(stock.mutualfund_holders, "mutualfund_holders.json", ticker)
        save_to_json(stock.insider_transactions, "insider_transactions.json", ticker)
        save_to_json(stock.insider_purchases, "insider_purchases.json", ticker)
        save_to_json(stock.insider_roster_holders, "insider_roster_holders.json", ticker)
        
        # Get sustainability data
        save_to_json(stock.sustainability, "sustainability.json", ticker)
        
        # Get recommendations
        save_to_json(stock.recommendations, "recommendations.json", ticker)
        save_to_json(stock.recommendations_summary, "recommendations_summary.json", ticker)
        save_to_json(stock.upgrades_downgrades, "upgrades_downgrades.json", ticker)
        
        # Get analysts data
        save_to_json(stock.analyst_price_targets, "analyst_price_targets.json", ticker)
        save_to_json(stock.earnings_estimate, "earnings_estimate.json", ticker)
        save_to_json(stock.revenue_estimate, "revenue_estimate.json", ticker)
        save_to_json(stock.earnings_history, "earnings_history.json", ticker)
        save_to_json(stock.eps_trend, "eps_trend.json", ticker)
        save_to_json(stock.eps_revisions, "eps_revisions.json", ticker)
        save_to_json(stock.growth_estimates, "growth_estimates.json", ticker)
        
        # Get earnings dates
        save_to_json(stock.earnings_dates, "earnings_dates.json", ticker)

        # Get news
        save_to_json(stock.news, "news.json", ticker)

if __name__ == "__main__":
    tickers = ["RR.L",]  # Example list of tickers
    get_comprehensive_stock_data(tickers)