import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from psycopg2 import sql

def generate_ebay_url(product_name, page_number=1):
    base_url = 'https://www.ebay.co.uk/sch/i.html'
    params = {
        '_nkw': product_name.replace(' ', '+'),  
        '_sacat': '0',
        'LH_Auction': '1',
        'LH_PrefLoc': '1',  # Filter to UK only
        'rt': 'nc',
        'LH_Sold': '1',
        'LH_Complete': '1',
        '_ipg': '240',
        '_pgn': page_number  
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    url = f"{base_url}?{query_string}"
    return url

def get_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def parse(soup):
    excluded_words = ['broken', 'damaged', 'parts', 'repair', 'faulty']

    results = soup.find_all('div', {'class': 's-item__info clearfix'})
    productlist = []
    for item in results:
        title = item.find('div', {'class': 's-item__title'})
        price = item.find('span', {'class': 's-item__price'})
        sold_date = item.find('span', {'class': 'POSITIVE'})
        bids = item.find('span', {'class': 's-item__bids'})
        link = item.find('a', {'class': 's-item__link'})

        if title and any(word.lower() in title.text.lower() for word in excluded_words):
            continue
        
        if title and price and sold_date and bids and link:
            sold_date_text = sold_date.text.replace('Sold', '').strip()
            
            try:
                date = datetime.strptime(sold_date_text, '%d %b %Y')
            except ValueError:
                date = pd.NaT
            
            product = {
                'title': title.text,
                'soldprice': float(price.text.replace('£','').replace(',','').strip()),
                'solddate': date,
                'bids': bids.text,
                'link': link['href']
            }
            productlist.append(product)
            print(product)
    
    return productlist

def output(productlist):
    productsdf = pd.DataFrame(productlist)
    csv_path = 'F:/data/Completed projects/python_project/output.csv'
    productsdf.to_csv(csv_path, index=False)  # Adjust the path to where you want your output
    print(f'Saved to CSV at {csv_path}')
    return productsdf

def search_ebay():
    product_name = input("Enter the product name to search on eBay: ")
    total_pages = int(input("Enter the number of pages to scrape: "))

    all_productlist = []

    for page in range(1, total_pages + 1):
        print(f"Scraping page {page}...")
        url = generate_ebay_url(product_name, page)
        soup = get_data(url)
        productlist = parse(soup)
        all_productlist.extend(productlist) 
    productsdf = output(all_productlist)

    return productsdf

def create_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS ebay_data (
                id SERIAL PRIMARY KEY,
                title TEXT,
                soldprice FLOAT,
                solddate DATE,
                bids TEXT,
                link TEXT
            )
            """)
            conn.commit()
            print("Table created successfully or already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()

def insert_data_to_postgres(conn, productsdf):
    try:
        with conn.cursor() as cur:
            for _, row in productsdf.iterrows():
                cur.execute("""
                INSERT INTO ebay_data (title, soldprice, solddate, bids, link)
                VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['title'],
                    row['soldprice'],
                    row['solddate'],
                    row['bids'],
                    row['link']
                ))
            conn.commit()
            print("Data inserted successfully into PostgreSQL.")
    except Exception as e:
        print(f"Error inserting data into PostgreSQL: {e}")
        conn.rollback()

def main():
    productsdf = search_ebay()

    conn = psycopg2.connect(
        dbname="ebay", 
        user="owent", 
        password="owent", 
        host="localhost", 
        port="5432"
    )

    create_table(conn)

    insert_data_to_postgres(conn, productsdf)

    conn.close()

    df = pd.read_csv('F:/data/Completed projects/python_project/output.csv')  # Adjust the path here!
    df['solddate'] = pd.to_datetime(df['solddate'], errors='coerce')
    df = df.dropna(subset=['solddate'])

    df.replace([float('inf'), -float('inf')], pd.NA, inplace=True)

    sns.set(style='whitegrid')
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='solddate', y='soldprice', data=df)
    plt.title('Average Sold Price over Time')
    plt.xlabel('Sold Date')
    plt.ylabel('Average Sold Price (£)')
    plt.xticks(rotation=45)
    plt.show()

    plt.figure(figsize=(12, 6))
    sns.histplot(df['soldprice'], kde=True, bins=20, color='blue')
    plt.title('Sold Price Distribution')
    plt.xlabel('Sold Price (£)')
    plt.ylabel('Frequency')
    plt.show()

if __name__ == "__main__":
    main()
