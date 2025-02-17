import yfinance as yf
import pandas as pd
from tqdm import tqdm
import time
import json
from datetime import datetime, timedelta
import os
import logging

def read_tickers(file_path):
    return pd.read_csv(file_path, header=None)[0].tolist()

import json

def save_to_json(data, filename, ticker):
    folder_name = "lse_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    file_path = os.path.join(folder_name, filename)
    
    if isinstance(data, pd.DataFrame):
        json_data = data.to_json(orient='split', date_format='iso')
    elif isinstance(data, pd.Series):
        json_data = data.to_json(orient='split', date_format='iso')
    else:
        json_data = json.dumps(data, default=str)
    
    json_data = json.loads(json_data)
    json_data['ticker'] = ticker
    
    with open(file_path, 'w') as f:
        json.dump([json_data], f, indent=4)
    
    print(f"Data for {ticker} saved to {file_path}")




def get_comprehensive_stock_data(ticker):
    stock = yf.Ticker(f"{ticker}.L")
    
    try:
        # Get historical market data (2 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        hist = stock.history(start=start_date, end=end_date)
        
        # Reset index to make Date a column
        hist.reset_index(inplace=True)
        
        # Add ticker column
        #hist['Ticker'] = ticker
        hist['Date'] = hist['Date'].dt.tz_localize(None)
        # Get financial data
        financial_data = get_financial_data(stock)
        print(f"hist shape: {hist.shape}")

  
        print("0")
        fin_df = pd.DataFrame(financial_data)
        print("1")
        fin_df.index = pd.to_datetime(fin_df.index, format='%Y-%m-%d', errors='coerce')
        print("2")
        fin_df = fin_df.groupby(fin_df.index).first().sort_index()# This will keep the first occurrence of each date
        print("3")
        print(fin_df.index.min(), fin_df.index.max())
        duplicates = fin_df.index.duplicated()
        print(f"fin_df shape: {fin_df.shape}")
        print(f"fin_df index: {fin_df.index}")
        if duplicates.any():
            print(f"Duplicate indices found: {fin_df.index[duplicates]}")
        try:
            merged_df = pd.merge_asof(hist.sort_values('Date'), 
                                    fin_df.sort_index(), 
                                    left_on='Date', 
                                    right_index=True, 
                                    direction='backward')
            merged_df = merged_df.fillna(method='ffill').infer_objects(copy=False)
        except Exception as e:
            print(f"Error during merge: {str(e)}")
            print(f"hist index: {hist.set_index('Date').index}")
            print(f"fin_df index: {fin_df.index}")
        merged_df = merged_df.reset_index()
        
        # Add technical indicators and other features
        merged_df['SMA_50'] = merged_df['Close'].rolling(window=50).mean()
        merged_df['SMA_200'] = merged_df['Close'].rolling(window=200).mean()
        merged_df['RSI'] = calculate_rsi(merged_df['Close'])
        
        # Create lagged features
        for lag in [1, 5, 10, 20]:
            merged_df[f'Return_Lag_{lag}'] = merged_df['Close'].pct_change(lag)
        
        # Add target variable
        merged_df['Target'] = merged_df['Close'].pct_change(5).shift(-5)
        # Get insider transactions
        insider_transactions = stock.insider_transactions
        if isinstance(insider_transactions, pd.DataFrame) and not insider_transactions.empty:
            insider_transactions['Date'] = pd.to_datetime(insider_transactions['Start Date']).dt.tz_localize(None)
            insider_transactions = insider_transactions.set_index('Date')
            
            # Aggregate insider transactions by date
            insider_agg = insider_transactions.groupby(insider_transactions.index).agg({
                'Shares': 'sum',
                'Value': 'sum',
                'Insider': 'count'
            }).rename(columns={'Insider': 'Transaction_Count'})
            
            # Merge insider transactions with the main dataframe
            merged_df = pd.merge_asof(merged_df.sort_values('Date'), 
                                      insider_agg.sort_index(), 
                                      left_on='Date', 
                                      right_index=True, 
                                      direction='backward')
            
            # Fill NaN values with 0 for insider transaction columns
            for col in ['Shares', 'Value', 'Transaction_Count']:
                merged_df[f'Insider_{col}'] = merged_df[col].fillna(0)
                merged_df = merged_df.drop(col, axis=1)
            
            # Calculate cumulative insider transactions
            merged_df['Insider_Cumulative_Shares'] = merged_df['Insider_Shares'].cumsum()
            merged_df['Insider_Cumulative_Value'] = merged_df['Insider_Value'].cumsum()
            merged_df['Insider_Cumulative_Transactions'] = merged_df['Insider_Transaction_Count'].cumsum()    
            merged_df['Ticker'] = ticker
        print(f"merged_df shape: {merged_df.shape}")
        return merged_df
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def get_financial_data(stock):
    financial_data = {}
    for attr_name in ['income_stmt', 'balance_sheet', 'cashflow']:
        data = getattr(stock, attr_name)
        time.sleep(5)
        if isinstance(data, pd.DataFrame):
            # Transpose the DataFrame
            data = data.T
            data.index = pd.to_datetime(data.index)
            data = data.sort_index()
            # Add a prefix to column names to avoid conflicts
            data.columns = [f"{attr_name}:{col}" for col in data.columns]
            financial_data[attr_name] = data
    
    # Combine all financial data
    combined_data = pd.concat(financial_data.values(), axis=1)
    return combined_data

def get_insider_transactions(stock):
    insider_transactions = stock.insider_transactions
    if isinstance(insider_transactions, pd.DataFrame):
        return {
            'recent_insider_transactions': len(insider_transactions),
            'net_insider_shares': insider_transactions['Shares'].sum()
        }
    return {}


def calculate_rsi(prices, period=14):
    
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def debug_missing_values(stock, problematic_columns):
    financial_data = get_comprehensive_stock_data(stock)
    print(type(financial_data))
    for col in problematic_columns:
        print(f"Debugging column: {col}")
        
        # Check if the column exists in the DataFrame
        if col not in financial_data.columns:
            print(f"  Column '{col}' not found in the DataFrame")
            continue
        
        # Check for all missing values
        if financial_data[col].isnull().all():
            print(f"  All values in '{col}' are missing")
        else:
            # If not all values are missing, show some statistics
            print(f"  Missing values: {financial_data[col].isnull().sum()}")
            print(f"  Non-null count: {financial_data[col].count()}")
            print(f"  Unique values: {financial_data[col].nunique()}")
        
        # Check the original data source

        statement_type, column_name = col.split(':', 1)
        original_data = getattr(stock, statement_type)
        if isinstance(original_data, pd.DataFrame):
            if column_name in original_data.columns:
                print(f"  Original data for '{column_name}':")
                print(original_data[column_name].head())
            else:
                print(f"  '{column_name}' not found in original {statement_type}")
        else:
            print(f"  {statement_type} is not a DataFrame")
        
        print("\n")
def main():

    tickers = read_tickers('tickers.csv')
                            # Usage
    problematic_columns = [
            'balance_sheet:Cash Equivalents',
            'balance_sheet:Cash Financial',
            'cashflow:Short Term Debt Issuance',
            'cashflow:Net Other Investing Changes'
        ]

    all_data = pd.DataFrame()
    
    for ticker in tqdm(tickers, desc="Processing stocks"):
        #debug_missing_values(ticker, problematic_columns)
        stock_data = get_comprehensive_stock_data(ticker)

        
        if stock_data is not None:
            all_data = pd.concat([all_data, stock_data], ignore_index=True)
        time.sleep(2)  # Add a delay to avoid rate limiting
    
    # Save all data to a single CSV file
    all_data.to_csv('lse_stocks_comprehensive_data_full.csv', index=False)
    
    # Print information about the dataset
    print(all_data.info())
    print(all_data.describe())
    print(all_data.columns)
    print(f"Total stocks processed: {len(all_data['Ticker'].unique())}")
    print(f"Data saved to 'lse_stocks_comprehensive_data.csv'")
    
    # Print the first 10 rows
    print("\nFirst 10 rows of the data:")
    print(all_data.head(10))






if __name__ == "__main__":
    main()
    
    