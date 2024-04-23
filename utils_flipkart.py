import random
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import time
from collections import defaultdict

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

# def get_reviews(soup):
#     reviews = soup.find_all('div', {'class': ''})
#     return [review.text.strip() for review in reviews]

def get_rating(soup):
    rating = soup.find('div', {'class':'XQDdHH'})
    return rating.text.strip() if rating else "No rating found"

def get_description(soup):
    # description = soup.find_all('div', {'class':'yN+eNk w9jEaj'})
    # result = []
    # for desc in description:
    #     result.append(desc.text.strip())
    # return result
    description_div = soup.find('div', {'class': 'Xbd0Sd'})
    p_element = description_div.find_all('p')
    description = []
    for p in p_element:
        description.append(p.text)
    description = description[0].split('.') if description else "No description found"
    description = description[0:-1]
    return description

def get_image_url(soup):
    image = soup.find('img', {'class': '_0DkuPH'})
    image_url = image['src'] if image else "No image found"
    return image_url

def get_reviews(soup):
    reviews = soup.find_all('div', {'class': 'RcXBOT'})
    return [review.div.div.text for review in reviews if review.div and review.div.div and review.div.div]

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

def get_count_reviews(soup):
    span = soup.find('span', class_='Wphh3N')
    text = span.text.strip()
    ratings, reviews = text.split('&')
    ratings = ratings.strip()
    ratings = ratings.replace(',', '')
    ratings = int(ratings.split(' ')[0])
    return ratings

def get_average_rating(soup):
    rating = soup.find('div', {'class':'XQDdHH'})
    return rating.text.strip() if rating else "0"
def get_title(soup):
    title = soup.find('span', {'class':'B_NuCI'})
    return title.text.strip() if title else "No title found"
def get_price(soup):
    price = soup.find('div', {'class':'_30jeq3 _16Jk6d'})
    return price.text.strip() if price else "No price found"

def get_product_data(url):
    soup = scrape_data(url)
    title = get_title(soup)
    price = get_price(soup)
    link = url
    rating = get_rating(soup)
    description = get_description(soup)
    image_url = get_image_url(soup)
    reviews_url = generate_reviews_url(url)
    reviews = get_all_reviews(reviews_url)
    reviews = clean_reviews(reviews)
    count_reviews = get_count_reviews(soup)
    average_rating = get_average_rating(soup)

    return {
        "title": title,
        "price": price,
        "link": link,
        "reviews": reviews,
        "rating": rating,
        "description": description,
        "image_url": image_url,
        "count_reviews": count_reviews,
        "average_rating": average_rating
    }

def clean_reviews(reviews):
    cleaned_reviews = []
    for review in reviews:
        # review = review.replace('\n', ' ')
        # review = review.replace('\t', ' ')
        # review = review.replace('\r', ' ')
        # review = review.replace('  ', ' ')
        parts = review.split("READ MORE")
        review = parts[0]
        rating = review[0]
        review = rating + ' stars: ' + review[1:]
        cleaned_reviews.append(review)
    return cleaned_reviews

def get_data(key):
    url_flip = 'https://www.flipkart.com/search?q=' + str(
        key) + '&marketplace=FLIPKART&otracker=start&as-show=on&as=off'
    map = defaultdict(list)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    source_code = requests.get(url_flip, headers=headers)
    soup = BeautifulSoup(source_code.text, "html.parser")
    home = 'https://www.flipkart.com'
    products = {}
    i = 0
    for block in soup.find_all('div', {'class': 'tUxRFH'}):
        try:
            title, price, link = None, 'Currently Unavailable', None
            # print(block.prettify())
            if block.find('div', {'class': 'KzDlHZ'}):
                title = block.find('div', {'class': 'KzDlHZ'}).text
                # print("Title",title)
            if block.find('div', {'class': 'Nx9bqj _4b5DiR'}):
                price = block.find('div', {'class': 'Nx9bqj _4b5DiR'}).text
                # print("Price",price)
            if block.find('a', {'class': 'CGtC98'}):
                link = home + block.find('a', {'class': 'CGtC98'}).get('href')
                # print("Link",link)
            map[title] = [price, link]
            product_data = get_product_data(link)
            products[i] = {
                    "title": title, 
                    "price": price, 
                    "link": link,
                    "rating": product_data["rating"],
                    "description": product_data["description"],
                    "image_url": product_data["image_url"],
                    "reviews": product_data["reviews"],
                    "count_reviews": product_data["count_reviews"],
                    "average_rating": product_data["average_rating"]
                }
            i += 1
            if i == 10:
                break
        except:
            pass
    for block in soup.find_all('div', {'class': 'slAVV4'}):
        try:
            # print("Block",block.prettify())
            title, price, link = None, 'Currently Unavailable', None
            if block.find('a', {'class': 'wjcEIp'}):
                title = block.find('a', {'class': 'wjcEIp'}).get('title')
                print("Title",title)
            if block.find('div', {'class': 'Nx9bqj'}):
                price = block.find('div', {'class': 'Nx9bqj'}).text
                print("Price",price)
            if block.find('a', {'class': 'VJA3rP'}):
                link = home + block.find('a', {'class': 'VJA3rP'}).get('href')
                print("Link",link)
            map[title] = [price, link]
            product_data = get_product_data(link)
            products[i] = {
                    "title": title, 
                    "price": price, 
                    "link": link,
                    "rating": product_data["rating"],
                    "description": product_data["description"],
                    "image_url": product_data["image_url"],
                    "reviews": product_data["reviews"],
                    "count_reviews": product_data["count_reviews"],
                    "average_rating": product_data["average_rating"]
                }
            # print("URL",products[i]['image_url'])
            i += 1
            if i == 10:
                break
        except:
            pass
    return products
        
    