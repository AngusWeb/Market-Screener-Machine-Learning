import requests
from lxml import html
import csv
import sys

# URL of the webpage (replace with the actual URL)
url = "https://www.stockchallenge.co.uk/ftse.php"

try:
    # Send a GET request to the webpage
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML content
    tree = html.fromstring(response.content)

    # Use XPath to find all ticker elements (EPIC column)
    tickers = tree.xpath('//table[@bgcolor="#e0e0e0"]/tr[position()>1]/td[2]/text()')

    print(f"Found {len(tickers)} raw ticker elements")

    # Remove any leading/trailing whitespace from tickers
    tickers = [ticker.strip() for ticker in tickers if ticker.strip()]

    print(f"After cleaning, found {len(tickers)} tickers")

    # Print the first few tickers (if any)
    print("First few tickers:", tickers[:5])

    # Write tickers to a CSV file
    with open('tickers.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Ticker'])  # Header
        for ticker in tickers:
            writer.writerow([ticker])

    print(f"Scraped {len(tickers)} tickers and saved to tickers.csv")

except requests.RequestException as e:
    print(f"Error fetching the webpage: {e}", file=sys.stderr)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)