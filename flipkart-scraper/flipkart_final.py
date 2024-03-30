from bs4 import BeautifulSoup
import requests
from difflib import get_close_matches
import webbrowser
from collections import defaultdict
import random
import csv
from utils import get_product_data

def get_data(key):
    url_flip = 'https://www.flipkart.com/search?q=' + str(
        key) + '&marketplace=FLIPKART&otracker=start&as-show=on&as=off'
    map = defaultdict(list)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    source_code = requests.get(url_flip, headers=headers)
    soup = BeautifulSoup(source_code.text, "html.parser")
    home = 'https://www.flipkart.com'
    products = []
    for block in soup.find_all('div', {'class': '_2kHMtA'}):
        title, price, link = None, 'Currently Unavailable', None
        for heading in block.find_all('div', {'class': '_4rR01T'}):
            title = heading.text
        for p in block.find_all('div', {'class': '_30jeq3 _1_WHN1'}):
            price = p.text[1:]
        for l in block.find_all('a', {'class': '_1fQZEK'}):
            link = home + l.get('href')
        map[title] = [price, link]
        product_data = get_product_data(link)
        products.append(
            {
                "title": title, 
                "price": price, 
                "link": link,
                "rating": product_data["rating"],
                "description": product_data["description"],
                "image_url": product_data["image_url"],
                "reviews": product_data["reviews"]
            }
        )
    return products
        
    