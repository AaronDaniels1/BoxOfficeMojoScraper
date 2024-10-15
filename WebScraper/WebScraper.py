"""This will be my webscraper for Box Office Mojo"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import datetime

import smtplib
import uuid
from concurrent.futures import ThreadPoolExecutor

# Connect to website

base_url = "https://www.boxofficemojo.com/date/"

headers = {'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

# Start and end dates for scraping
start_date = datetime.datetime(1977, 5, 1)
end_date = datetime.datetime.now() - datetime.timedelta(days=3)  # Five days ago from today

def get_daily_box_office_totals(url):
    """Scrapes daily box office totals for a specific date."""
    # Fetch the webpage
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return None

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table with the daily box office totals
    table = soup.find('table')

    if not table:
        print(f"No data found for {url}")
        return None

    # Extract table headers
    headers = [th.text.strip() for th in table.find_all('th')]

    # Extract table rows
    rows = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        cells = row.find_all('td')
        row_data = [cell.text.strip() for cell in cells]
        rows.append(row_data)

    return headers, rows

# List to hold all data
all_data = []
headers = None

"""with ThreadPoolExecutor(max_workers=10) as executor:
    dates = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    results = list(executor.map(get_daily_box_office_totals, dates))

for result in results:
    if result:
        headers, rows = result
        all_data.extend(rows)"""

# Loop through each date in the range and scrape data
current_date = start_date
while current_date <= end_date:
    formatted_date = current_date.strftime("%Y-%m-%d")
    url = f"{base_url}{formatted_date}/"
    print(url)
    print(f"Scraping data for {formatted_date}")

    # Get data for the specific date
    result = get_daily_box_office_totals(url)
    if result:
        headers, rows = result
        # Append date information to each row
        for row in rows:
            row.insert(0, formatted_date)  # Insert date as the first column
        all_data.extend(rows)
    current_date += datetime.timedelta(days=1)

    # Save to Excel
if all_data:
    headers.insert(0, "Date")  # Insert 'Date' as the first header
    df = pd.DataFrame(all_data, columns=headers)
    
    # Drop unwanted columns if they exist
    columns_to_drop = ["TD", "YD", "%± YD", "%± LW", "Avg", "New This Day","Estimated"]
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Add unique ID
    df.insert(0, "ID", [str(uuid.uuid4()) for _ in range(len(df))]) 

    # Save to Excel
    df.to_excel("all_box_office_totals.xlsx", index=False)
    print("Data saved to 'all_box_office_totals.xlsx'")
else:
    print("No data to save.")