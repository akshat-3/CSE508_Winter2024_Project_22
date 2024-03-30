import random
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import time

def specific_string(length):
    sample_string = 'pqrstuvwxyaksdjhkasdlkjqluwoelkansldknc' # define the specific string
    result = ''.join((random.choice(sample_string)) for x in range(length))
    return result

headers = {
    'User-Agent': specific_string(random.randint(1,999)),
    'From': specific_string(random.randint(1,999))
}
cookies = {
    'session-id': '261-1163646-2292460',
    'session-id-time': '2082787201l',
    'i18n-prefs': 'INR',
    'ubid-acbin': '262-5280853-8370053',
    'session-token': '0Yx/sl7jsWUnMhSpZuNhnhoitPCy/P87wflbutp1yQrh8Yb7bcu/iy3Pq6+mwfvbHPt5levtC+EpVnMKlrXlieqJfd4SHBcO9/fKvQVmGwljmQpqwB64900L33gAXKg3/CY2GA19uLkuW5syRtu0GcyU6SvUfupuV4+E0Rd4U5kuWuzVWlNYH/uGVOJA2vhioSLTEh56fG2jrmtzmwZXX9qsZVVQjGaaqT729Q99uP8=',
    'csm-hit': 'tb:s-RCA08544A2YQCT2J63XM|1684211284757&t:1684211285532&adb:adblk_no',
}

def scrape_data(url):
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    # response = requests.get(url, headers=headers, cookies=cookies)
    # page_html = response.text
    soup = BeautifulSoup(page_html, 'html.parser')
    return soup

def get_reviews(soup):
    reviews = soup.find_all('div', {'class': '_6K-7Co'})
    return [review.text.strip() for review in reviews]

def get_rating(soup):
    rating = soup.find('div', {'class':'_3LWZlK'})
    return rating.text.strip() if rating else "No rating found"

def get_description(soup):
    description = soup.find('div', {'class':'_2o-xpa'})
    return description.text.strip() if description else "No description found"

def get_image_url(soup):
    image = soup.find('img', {'class': 'q6DClP'})
    image_url = image['src'] if image else "No image found"
    return image_url

def get_reviews(soup):
    reviews = soup.find_all('div', {'class': 't-ZTKy'})
    return [review.div.div.text for review in reviews if review.div and review.div.div]

def get_all_reviews(url):
    soup = scrape_data(url)
    reviews = get_reviews(soup)
    return reviews

def generate_reviews_url(product_url):
    # Split the URL into parts
    parts = product_url.split('?')
    
    # Replace the query parameters with 'product-reviews'
    parts[1] = 'product-reviews'
    
    # Join the parts back together into a URL
    reviews_url = '?'.join(parts)
    
    return reviews_url

def get_product_data(url):
    soup = scrape_data(url)
    rating = get_rating(soup)
    description = get_description(soup)
    image_url = get_image_url(soup)
    reviews_url = generate_reviews_url(url)
    reviews = get_all_reviews(reviews_url)

    return {
        "reviews": reviews,
        "rating": rating,
        "description": description,
        "image_url": image_url
    }