import datetime
from download import download_url
from md5 import md5
import random
import requests
import sqlite3
from secrets import user_info
from pathlib import Path
import xml.etree.ElementTree as ET

URL = 'https://scihub.copernicus.eu/dhus/search?q=*'
today = datetime.date.today()
past_days =  today - datetime.timedelta(days=2)

with requests.Session() as s:
    s.auth = user_info()
    
    params = {'beginposition': today.strftime('%Y-%m-%dT%H:%M:%S.%fz'), 
              'endposition':past_days.strftime('%Y-%m-%dT%H:%M:%S.%fz'), 
              'start': '0'}
    try: 
        response = s.get(URL, params=params,timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        quit()
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        quit()
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        quit()
    except requests.exceptions.RequestException as err:
        print ("Unknown error:",err)
        quit()
    print(f'Retriving {response.url}')
    print(f'Server responded with {response.status_code} status code')
    
    data = response.text
    root = ET.fromstring(data)
    ns = {'default': 'http://www.w3.org/2005/Atom'}
    records = root.find('default:subtitle', ns)
    range_list = [word for word in records.text.split() if word.isnumeric()]
    number_of_products = max(map(int, range_list))//100
    
    random_products = list()
    href = list()
    while len(random_products) < 3:
        num = random.randint(1, number_of_products)
        params['start'] = str(num)
        try:
            new_response = s.get(URL, params=params, timeout=15)
            print(f"Fetching {new_response.url}")
            new_response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            quit()
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            quit()
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            continue
        except requests.exceptions.RequestException as err:
            print ("Unknown error:",err)
            continue    
        if new_response.status_code == 200:
            random_products.append(num)
            data = new_response.text
            prod_root = ET.fromstring(data)
            product = prod_root.find('default:entry', ns)
            download_link = product.find('default:link', ns)
            prod_url = download_link.attrib
            href.append(prod_url)
    print('Fetched product numbers are: ', random_products)    
    
    conn = sqlite3.connect('Sentinel.sqlite')
    cur = conn.cursor()
        
    cur.executescript('''
        DROP TABLE IF EXISTS Products;
            
        CREATE TABLE Products (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
            filename TEXT UNIQUE,
            path TEXT,
            md5sum TEXT UNIQUE
            );
        ''')

    current_path = Path(__file__).parent.absolute()
    for i in range(len(href)):
        print("Dowloading file")
        zip_file = download_url(s, href[i]['href'], str(current_path)+'/')
        path = str(current_path) + zip_file
        print(path)
        print("Complete downloading file: ", zip_file)
        prod_link = href[i]['href']
        prod_id = prod_link[:-6]
        prod_checksum = prod_id + "Checksum/Value/$value"
        print("Getting file checksum")
        checksum = s.get(prod_checksum)
        dowloaded_file_checksum = md5(path)

        if checksum.text == dowloaded_file_checksum:
            print("Checksums match")
            cur.execute('''INSERT OR IGNORE INTO Products (filename, path, md5sum)
                VALUES ( ? , ?, ? )''', ( zip_file, path, dowloaded_file_checksum) )
            conn.commit()
        else: 
            print("Couldn't match file checksum")
    cur.close()
    conn.close()
        