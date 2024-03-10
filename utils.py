
import random
from PIL import Image
import re
import requests
from io import BytesIO
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from requests import Session
nltk.download('vader_lexicon', quiet = True)


#initialize the session
session = Session()

def specific_string(length):
    sample_string = 'pqrstuvwxyaksdjhkasdlkjqluwoelkansldknc' # define the specific string
    # define the condition for random string
    result = ''.join((random.choice(sample_string)) for x in range(length))
    return result

cookies = {
    'session-id': '261-1163646-2292460',
    'session-id-time': '2082787201l',
    'i18n-prefs': 'INR',
    'ubid-acbin': '262-5280853-8370053',
    'session-token': '0Yx/sl7jsWUnMhSpZuNhnhoitPCy/P87wflbutp1yQrh8Yb7bcu/iy3Pq6+mwfvbHPt5levtC+EpVnMKlrXlieqJfd4SHBcO9/fKvQVmGwljmQpqwB64900L33gAXKg3/CY2GA19uLkuW5syRtu0GcyU6SvUfupuV4+E0Rd4U5kuWuzVWlNYH/uGVOJA2vhioSLTEh56fG2jrmtzmwZXX9qsZVVQjGaaqT729Q99uP8=',
    'csm-hit': 'tb:s-RCA08544A2YQCT2J63XM|1684211284757&t:1684211285532&adb:adblk_no',
}



#WORKING FUNCTIONS

def scrape_data(url):
    try:
        headers = {
                    'User-Agent': specific_string(random.randint(1,999)),
                    'From': specific_string(random.randint(1,999))
        }
        response = session.get(url, headers=headers,cookies=cookies)
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except:
        return BeautifulSoup()

def get_product_details(soup):
    product_details = {}
    try:
        name_element = soup.find('span', {'id':'productTitle'})
        if name_element is not None:
            product_details['name'] = name_element.string.strip()

        price_element = soup.find('span', {'class':'a-offscreen'})
        if price_element is not None:
            product_details['price'] = price_element.string.strip()

        return product_details
    except:
        return product_details
    
# 3. Scrape reviews
def get_all_reviews(url):
    reviews = []
    try:
        headers = {
                    'User-Agent': specific_string(random.randint(1,999)),
                    'From': specific_string(random.randint(1,999))
        }

        response = requests.get(url, headers=headers, cookies = cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews.extend([review.text.strip() for review in soup.find_all('span', {'data-hook': 'review-body'})])
        return reviews
    except:
        return reviews
    
def scrape_reviews(url):
    try:
        headers = {
                    'User-Agent': specific_string(random.randint(1,999)),
                    'From': specific_string(random.randint(1,999))
        }

        response = requests.get(url, headers=headers, cookies=cookies)
        final_url = response.url  # Get the final URL after all redirects
        reviews_url = final_url.replace("/dp/", "/product-reviews/") + "?pageNumber=" + str(1)
        # reviews_url = url.replace("/sspa/", "/product-reviews/") + "?pageNumber=" + str(1)
        return get_all_reviews(reviews_url)
    except:
        return []

# 4. NLP-based review analysis
def analyze_reviews(reviews):
    sentiment_analyzer = SentimentIntensityAnalyzer()
    compound_scores = []
    for review in reviews:
        sentiment_score = sentiment_analyzer.polarity_scores(review)
        compound_scores.append(sentiment_score['compound'])
    if len(compound_scores) == 0:
        return 0
    average_compound_score = sum(compound_scores) / len(compound_scores)
    return average_compound_score

def get_about_this_item(soup):
    try:
        about_item = soup.find('h1', {'class':'a-size-base-plus a-text-bold'}).text
        item_details = [li.text.strip() for li in soup.find_all('li', {'class':'a-spacing-mini'})]

        return about_item, item_details
    except:
        return [], []



def search_amazon(product_name):
    try:
        # Replace spaces in the product name with '+'
        product_name = product_name.replace(' ', '+')

        # Create the URL for the search results page
        url = f"https://www.amazon.in/s?k={product_name}"

        # # Define the proxies
        # proxies = {
        #     "http": "http://10.10.1.10:3128",
        #     "https": "http://10.10.1.10:1080",
        # }
        headers = {
                    'User-Agent': specific_string(random.randint(1,999)),
                    'From': specific_string(random.randint(1,999))
        }

        # Send a GET request to the Amazon server
        #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(url, cookies = cookies, headers=headers)

        # Parse the response text with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all product links on the search results page
        product_links = soup.find_all('a', {'class': 'a-link-normal a-text-normal'})

        # Extract the href attribute of each link and prepend 'https://www.amazon.com' to get the full URL
        product_urls = ['https://www.amazon.in' + link['href'] for link in product_links]
        return product_urls
    except:
        return []
# Test the function
# product_urls = search_amazon('iphone')
# for url in product_urls:
#     print(url)



def get_soup(params, page_number):
    try:
        params['page'] = str(page_number)
        headers = {
                'User-Agent': specific_string(random.randint(1,999)),
                'From': specific_string(random.randint(1,999))
        }
        response = requests.get('https://www.amazon.in/s', params=params, cookies=cookies, headers=headers)
        return BeautifulSoup(response.text, 'html.parser')
    except:
        return BeautifulSoup()
    
def get_star_elements(soup):
    try:
        return soup.find_all(class_='a-icon-star-small')
    except:
        return []
    
def get_price_and_image_url(url):
    try:
        headers = {
                    'User-Agent': specific_string(random.randint(1,999)),
                    'From': specific_string(random.randint(1,999))
        }

        response = requests.get(url, headers=headers, cookies = cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        price_element = soup.find('span', {'class':'a-offscreen'})
        if price_element is not None:
            price = price_element.string.strip()    
        script_element = soup.find('script', text=re.compile('var iUrl'))

        # Extract the image URL from the script element
        if script_element is not None:
            match = re.search(r'var iUrl = "(.*?)";', script_element.string)
            if match:
                image_url = match.group(1)
            else:
                image_url = None
        else:
            image_url = None
        return price, image_url
    except:
        return None, None

def get_item_from_star_element(star_element):
    try:
        item = star_element.parent.parent.parent.parent.parent.parent.parent.parent.parent
        a_tag = item.find('a', class_='a-link-normal')
        if a_tag is not None:
            url = 'https://www.amazon.in' + a_tag.get('href')
        else:
            url = None
        return item, url
    except:
        return None, None