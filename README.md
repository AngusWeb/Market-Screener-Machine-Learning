# Market Screener Project

The **Market Screener Project** is a Python-based machine learning application designed to screen stocks using financial data. The project collects historical stock data with the Yahoo Finance package, processes and enhances the data with various technical and fundamental indicators, and trains predictive models using algorithms like XGBoost. In addition, it features a web scraper that extracts real-time financial information from [marketscreener.com](https://www.marketscreener.com/) to apply the developed models to any stock.

## Table of Contents

- [Overview](#overview)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Data Collection](#data-collection)
  - [Data Analysis & Model Training](#data-analysis--model-training)
  - [Web Scraping](#web-scraping)
- [Customisation & Future Work](#customisation--future-work)

## Overview

The goal of this project is to build a basic market screener that:
- **Collects training data** using the Yahoo Finance package.
- **Develops and tests financial models** (e.g., using XGBoost) within Jupyter Notebooks.
- **Extracts real-time stock data** from marketscreener.com via web scraping.
- **Applies predictive models** to forecast stock prices or financial metrics.

## Technologies Used

- **Programming Language:** Python
- **Data Collection:** [yfinance](https://pypi.org/project/yfinance/)
- **Notebooks:** Jupyter Notebook
- **Web Scraping:** `requests`, [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** XGBoost, Scikit-learn
- **Visualisation:** Matplotlib, Seaborn
- **Utilities:** tqdm, logging

### Data Collection

- **Update Tickers:**  
  Ensure `tickers.csv` contains the list of stock tickers you wish to analyse.

- *Data Collection Script:**  
  The `yahoo_dataset.py` script collects historical stock data along with key financial information from Yahoo Finance. Run:
  
  This script downloads historical data, calculates technical indicators (e.g., SMA, RSI), merges financial statements, and saves the processed data as CSV/JSON files.

### Data Analysis & Model Training

*   **Open the Jupyter Notebook:** The main\_project.ipynb notebook contains steps for:
    
    *   Loading the processed data.
        
    *   Visualising missing values and data distributions.
        
    *   Feature engineering (e.g., computing financial ratios, moving averages, lagged returns).
        
    *   Splitting the dataset into training, validation, and testing sets.
        
    *   Training an XGBoost regression model.
        
    *   Evaluating the model with metrics like Mean Squared Error and R-squared.
### Web Scraping

*   scrapper\_test.py - The script outputs the scraped data to a CSV file (output.csv) which can be used for further analysis or to update your predictive models.
### Customisation & Future Work
--------------------------

*   **Adding More Stocks:** Simply add additional tickers to tickers.csv.
    
*   **Enhancing Feature Engineering:** Modify or add technical indicators and financial ratios in the notebooks as needed.
    
*   **Model Improvements:** Experiment with different machine learning models, hyperparameters, or ensemble methods.
    
*   **Scraping Adjustments:** Adapt the web scraping logic in scrapper\_test.py if marketscreener.com updates its page structure.
