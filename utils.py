
import random
import streamlit as st
st.title('IR Project')

input_string = st.text_input('Enter a string')

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

headers = {
            'User-Agent': specific_string(random.randint(1,999)),
            'From': specific_string(random.randint(1,999))
}

# Python
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

# 1. Web scraping/crawling
def scrape_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers,cookies=cookies)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# 2. Data collation
def get_product_details(soup):
    product_details = {}

    name_element = soup.find('span', {'id':'productTitle'})
    if name_element is not None:
        product_details['name'] = name_element.string.strip()

    price_element = soup.find('span', {'class':'a-offscreen'})
    if price_element is not None:
        product_details['price'] = price_element.string.strip()

    return product_details

# 3. Scrape reviews
def get_reviews(soup):
    reviews = soup.find_all('span', {'data-hook': 'review-body'})
    return [review.text.strip() for review in reviews]

# 4. NLP-based review analysis
def analyze_reviews(reviews):
    sentiment_analyzer = SentimentIntensityAnalyzer()
    for review in reviews:
        sentiment_score = sentiment_analyzer.polarity_scores(review)
        print(f'Review: {review}\nSentiment Score: {sentiment_score}\n')


def get_about_this_item(soup):
    about_item = soup.find('h1', {'class':'a-size-base-plus a-text-bold'}).text
    item_details = [li.text.strip() for li in soup.find_all('li', {'class':'a-spacing-mini'})]

    return about_item, item_details


# Example usage
# url = 'https://www.amazon.in/Apple-iPhone-14-128GB-Midnight/dp/B0BDHX8Z63/ref=sr_1_10?dib=eyJ2IjoiMSJ9.eFa-TvbcC_zjCq_5PD2KOzq8FGFIoVfOOaz8akTXGASZDy9nMmG7fyQJcWpPDBvtZ_Q4w_WRrvCwz5nTc7cjiwnjiN969vgOAEeBN5IeypIRY6ZnKwtTdNRE5rEqe2XjmXtADrNke09Lb5INgZrsDLXgF72BwL5ou7M20nbSpiHtY9kO9J-9xgQYBUCEzxJam4p1t8E0dfv1ygBg0JlbtmMdnx4NcQr-9Bblv5Aa7OM.zSPJUgBI4O4UUlGQVih6CTAxgsEua7PamyEVoXpw1is&dib_tag=se&keywords=iphone&qid=1709754318&sr=8-10'


import requests
from bs4 import BeautifulSoup

def search_amazon(product_name):
    # Replace spaces in the product name with '+'
    product_name = product_name.replace(' ', '+')

    # Create the URL for the search results page
    url = f"https://www.amazon.in/s?k={product_name}"

    # # Define the proxies
    # proxies = {
    #     "http": "http://10.10.1.10:3128",
    #     "https": "http://10.10.1.10:1080",
    # }

    # Send a GET request to the Amazon server
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)

    # Parse the response text with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all product links on the search results page
    product_links = soup.find_all('a', {'class': 'a-link-normal a-text-normal'})

    # Extract the href attribute of each link and prepend 'https://www.amazon.com' to get the full URL
    product_urls = ['https://www.amazon.in' + link['href'] for link in product_links]
    return product_urls

# Test the function
product_urls = search_amazon('iphone')
for url in product_urls:
    print(url)



def get_soup(params, page_number):
    params['page'] = str(page_number)
    response = requests.get('https://www.amazon.in/s', params=params, cookies=cookies, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')

def get_star_elements(soup):
    return soup.find_all(class_='a-icon-star-small')



def get_item_from_star_element(star_element):
    item = star_element.parent.parent.parent.parent.parent.parent.parent.parent.parent
    a_tag = item.find('a', class_='a-link-normal')
    if a_tag is not None:
        url = 'https://www.amazon.in' + a_tag.get('href')
    else:
        url = None
    return item, url

def get_data(key):
    params = {
    'k': key,
    }
    page = get_soup(params, 1)

    elements = get_star_elements(page)
    for index, element in enumerate(elements):
        item, url = get_item_from_star_element(element)
        image = item.find('img', class_='s-image')
        st.image(image['src'], caption=url)  # Display the product image and URL

        soup = scrape_data(url)
        product_details = get_product_details(soup)
        st.write(product_details)  # Display the product details

        description = get_about_this_item(soup)
        st.write(f'About this item: {description}')  # Display the "About this item" section

        reviews = get_reviews(soup)
        st.write(reviews)  # Display the reviews
        analyze_reviews(reviews)

if st.button('Find'):
    get_data(input_string)