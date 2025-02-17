import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import html

ticker = 'MEMSCAP'
tickerurl = f'{ticker}-16275'
# URL of the webpage containing the table
url = f'https://uk.marketscreener.com/quote/stock/{tickerurl}/finances-income-statement/'

# Headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

cookies = {
    'sessionid': 'PHPSESSID=gsirpggdo55qq7q1mknkj17jgq; pv_r0_rand=12; zbconnect=otty4000%40gmail.com; rappelcookie=1; zb_membre=1; UTM_intern=%7B%22date%22%3A%222024-09-06%2016%3A14%3A43%22%2C%22id_utm_lien%22%3A%2247459551%22%7D; lc=en_GB; zb_auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IkwzbFZkbFkxUXpKaVJUWnZWVWw0WXpSWlMxQklRVDA5IiwiaWF0IjoxNzI3NTM1NTc3fQ.LvWAtGUN2YwnDLPoq2NSmepp3eUw_9C4iVy0GM_fVd4; pv_r0_date=2024-09-21; _lr_geo_location_state=ENG; _lr_geo_location=GB; hmv=8c34efa9c8a4453d9a08956d5ddac03e4dfd841a; pv_r0=6',
    # Add other cookies as needed
}

# Send a GET request to the URL
response = requests.get(url, headers=headers, cookies=cookies)
# Save the response content to a text file
with open("response_content.txt", "w", encoding="utf-8") as file:
    file.write(response.text)
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize variables to store fiscal periods and data
fiscal_periods = set()
data_dict = {}

# Find all rows that contain the data
rows = soup.find_all('tr', class_='txt-s1') + soup.find_all('tr', class_='txt-s1 bg-grey-light')

# Iterate over each row to extract data
for tr in rows:
    # Extract the row label (e.g., 'Revenues')
    p = tr.find('p', class_='c')
    if p:
        row_label = p.get_text(strip=True)
    else:
        continue

    tds = tr.find_all('td')
    if row_label not in data_dict:
        data_dict[row_label] = {}

    # Iterate over each cell in the row
    for td in tds:
        span = td.find('span', class_='js-currency-type')
        if span and 'data-raw' in span.attrs and 'data-date' in span.attrs:
            data_raw = span['data-raw']
            date = span['data-date']
            fiscal_period = date.split('-')[0]  # Extract the year from the date
            fiscal_periods.add(fiscal_period)
            data_dict[row_label][fiscal_period] = data_raw
        else:
            # If data is not available, you can choose to set a default value like None or ''
            pass

# Now, extract data from 'div's with class 'chart chart--h250 media--169 financial-chart'
divs = soup.find_all('div', class_='chart chart--h250 media--169 financial-chart')

for div in divs:
    data_fct_attr = div.get('data-fct-attr')
    if data_fct_attr:
        # Unescape HTML entities
        data_fct_attr = html.unescape(data_fct_attr)
        # Parse JSON
        try:
            data_dict_json = json.loads(data_fct_attr)
        except json.JSONDecodeError:
            continue  # Skip if JSON is invalid
        serieName = data_dict_json.get('serieName')
        categories = data_dict_json.get('categories')
        data_values = data_dict_json.get('data')
        if serieName and categories and data_values:
            row_label = serieName.strip()
            # Map categories to data_values
            data_points = dict(zip(map(str, categories), data_values))
            # Add to data_dict
            if row_label not in data_dict:
                data_dict[row_label] = {}
            data_dict[row_label].update(data_points)
            # Add fiscal periods
            fiscal_periods.update(map(str, categories))

# Sort the fiscal periods
fiscal_periods = sorted(fiscal_periods)

# Prepare data for the DataFrame
rows_list = []
for period in fiscal_periods:
    row = {'Fiscal Period': period}
    for label in data_dict.keys():
        value = data_dict[label].get(period)
        row[label] = value
    rows_list.append(row)

# Create a DataFrame
df = pd.DataFrame(rows_list)
df['Ticker'] = ticker

df = df.rename(columns={'Fiscal Period': 'Date'})
# Reorder columns to place 'Fiscal Period' first
#columns = ['Fiscal Period'] + [label for label in data_dict.keys()]
#df = df[columns]

# Save the DataFrame to a CSV file
df.to_csv('output.csv', index=True)

print("Data has been saved to 'output.csv'.")
