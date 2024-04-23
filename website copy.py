from utils_amazon import *
import utils_flipkart

from CompetitiveAnalysis import *
import streamlit as st
import time
import pickle
import os

st.markdown('### Group 22 IR Project')
st.markdown('#### E-Commerce Competitive Analysis System')
st.markdown('Search for a product on Amazon and Flipkart')
key = st.text_input('Enter the product name')

from concurrent.futures import ThreadPoolExecutor
import requests
from PIL import Image
from io import BytesIO
import concurrent.futures

def process_element(index, element):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            item, url = get_item_from_star_element(element)
            image = item.find('img', class_='s-image')
            response = requests.get(image['src'])
            img_pil = Image.open(BytesIO(response.content))

            soup = scrape_data(url)
            product_details = get_product_details(soup)

            description = get_about_this_item(soup)

            reviews = scrape_reviews(url)
            average_compound_score = analyze_reviews(reviews)
            product_detail = [product_details['name'], " ".join(description[1]), img_pil, url]
            all_detail = [product_details['name'], product_details['price'], description[0], description[1], average_compound_score, reviews,url, image['src'], 'Amazon', product_details['bought'], product_details['average_rating'], product_details['total_reviews']]
            return index, product_detail, all_detail
        except:
            if attempt < max_retries:  # i is zero indexed
                max_retries -= 1
                time.sleep(2)  # wait for 2 seconds before trying again
                continue
            else:
                return index, [], []
            
def process_element_flipkart(data):
    # product_detail = [product_details['name'], " ".join(description[1]), img_pil, url]
    # all_detail = [product_details['name'], product_details['price'], description[0], description[1], average_compound_score, reviews,url, image['src']]
    products_detail = {}
    all_products_detail = {}
    print("lengthhh", len(data))
    for i in range(len(data)):
        product_detail = []
        all_detail = []
        product_detail.append(data[i]['title'])
        product_detail.append(" ".join(data[i]['description']))
        try:
            response = requests.get(data[i]['image_url'])
            img_pil = Image.open(BytesIO(response.content))
        except:
            img_pil = None
        product_detail.append(img_pil)
        product_detail.append(data[i]['link'])
        products_detail[i] = product_detail
        
        all_detail.append(data[i]['title'])
        all_detail.append(data[i]['price'])
        all_detail.append(data[i]['description'])
        all_detail.append(data[i]['description'])
        average_compound_score = analyze_reviews(data[i]['reviews'])
        all_detail.append(average_compound_score)
        all_detail.append(data[i]['reviews'])
        all_detail.append(data[i]['link'])
        all_detail.append(data[i]['image_url'])
        all_detail.append('Flipkart')
        all_detail.append(None)
        all_detail.append(data[i]['average_rating'])
        all_detail.append(data[i]['count_reviews'])
        all_products_detail[i] = all_detail
    return products_detail, all_products_detail
   
def get_flipkart_data(key):
    data = utils_flipkart.get_data(key)
    return data
  
def get_data(key):
    with st.spinner('Searching for products...'):
        params = {
        'k': key,
        }
        page = get_soup(params, 1)

        elements = get_star_elements(page)
        #get first 10 elements
        elements = elements[:10]        
        product_dict_amazon = {}
        all_detail_product_amazon = {}

        product_dict_flipkart = {}
        all_detail_product_flipkart = {}

        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Use list comprehension to create a list of futures
            futures = [executor.submit(process_element, index, element) for index, element in enumerate(elements)]

            # Wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                index, product_detail, all_detail = future.result()
                product_dict_amazon[index] = product_detail
                all_detail_product_amazon[index] = all_detail
        
        #start flipkart indexing after amazon
        indexy = len(product_dict_amazon)
        flipkart_data = get_flipkart_data(key)
        # print(flipkart_data)
        product_detail_flipkart, all_detail_flipkart = process_element_flipkart(flipkart_data)

        for i in range(len(product_detail_flipkart)):
            product_dict_flipkart[indexy] = product_detail_flipkart[i]
            all_detail_product_flipkart[indexy] = all_detail_flipkart[i]
            indexy+=1
        
        # print(flipkart_data)
        # print(product_dict_amazon)
        # print(all_detail_product_amazon)
        print(product_dict_flipkart.keys())
        print(product_dict_amazon.keys())
        print(len(product_dict_amazon), len(product_dict_flipkart))
        product_dict = {}
        all_detail_product = {}
        #merge one amazon then one flipkart
        iterator = 0
        for i in range(len(product_dict_amazon)):
            product_dict[iterator] = product_dict_amazon[i]
            all_detail_product[iterator] = all_detail_product_amazon[i]
            iterator +=2
        
        iterator = 1
        for i in range(len(product_dict_flipkart)):
            product_dict[iterator] = product_dict_flipkart[i+len(product_dict_amazon)]
            all_detail_product[iterator] = all_detail_product_flipkart[i+len(product_dict_amazon)]
            iterator +=2


        # product_dict = {**product_dict_amazon, **product_dict_flipkart}
        print("total", len(product_dict))
        # all_detail_product = {**all_detail_product_amazon, **all_detail_product_flipkart}

        # print(product_dict)
        # print(all_detail_product)

        max_index, top_k_recommendations_dict = get_top_k_recommendations(key, product_dict)
        top_k_recommendations = top_k_recommendations_dict.keys()
        print("returned")
        # reviews = scrape_reviews(product_dict[max_index][3])
        # average_compound_score = analyze_reviews(reviews)
        # price, image_url = get_price_and_image_url(product_dict[max_index][3])
        # df = pd.DataFrame(reviews, columns=['Review'])
    
    with st.sidebar:
        try:
            param = all_detail_product[max_index][0]  # Replace with your actual parameter value
            st.markdown(f'''
                <div style="text-align: center;">
                    <a href="http://localhost:8502/?param={param}" target="_blank" style="text-decoration: none;">
                        <button style="
                            background-color: #000000; /* Black */
                            border: none;
                            color: white;
                            padding: 15px 32px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;
                            margin: 4px 2px;
                            cursor: pointer;
                            border-radius: 50%;
                            transition-duration: 0.4s; /* Adds animation */">
                        Review Analysis
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
            open('reviews.txt', 'w', encoding='utf-8').close()
            with open('reviews.txt', 'w', encoding='utf-8') as f:
                for line in all_detail_product[max_index][5]:
                    f.write(f"{line}\n")

            f.close()
            st.title("Your Product")
            st.markdown(f"<div style='text-align: center; padding: 10px;'><img src='{all_detail_product[max_index][7]}' style='width: 80%;'></div>",unsafe_allow_html=True)    
            st.markdown(f'<div style="text-align: center;"><a href="{all_detail_product[max_index][6]}" target="_blank">Go to product page</a>', unsafe_allow_html=True)   

            st.markdown(f"## {all_detail_product[max_index][0]}")
            st.markdown(f"### Price: {all_detail_product[max_index][1]}")
            if all_detail_product[max_index][9] == None:
                st.markdown(f"*Product Sales: Not Available*")
            else:
                st.markdown(f"*Product Sales: {all_detail_product[max_index][9]}*+ bought in the past month")            
            st.markdown(f"Average Rating on Website: {all_detail_product[max_index][10]}")
            st.markdown(f"Count of Total Reviews: {all_detail_product[max_index][11]}")
            st.markdown(f"### Average sentiment score: {all_detail_product[max_index][4]:.2f}")
            st.markdown(f"### Overall sentiment: {'positive' if all_detail_product[max_index][4] > 0 else 'negative' if all_detail_product[max_index][4] < 0 else 'neutral'}")
            with st.expander("About the Product"):
                st.write(pd.DataFrame(all_detail_product[max_index][3], columns=['About the Product']))
            with st.expander("Show Top Reviews"):
                st.dataframe(pd.DataFrame(all_detail_product[max_index][5], columns=['Review']))
        except:
            st.write("No product found")

    
    st.markdown(f"### Top {len(top_k_recommendations)} products by Competition")
    tab_labels = [f"Product {i+1}" for i in range(len(top_k_recommendations))]

    try:
        tabs = st.tabs(tab_labels)
        count = 0
        for index in top_k_recommendations:
            with tabs[count]:
                count+=1
                with st.spinner(f"Fetching data for {product_dict[index][0]}..."):
    
                    left_co, cent_co,last_co = st.columns(3)
                    with left_co:
                        st.image(all_detail_product[index][7], width=300)
                        st.markdown(f'<a href="{all_detail_product[index][6]}" target="_blank">Go to product page</a>', unsafe_allow_html=True)
                    with last_co:
                        st.markdown(f"Source: {all_detail_product[index][8]}")
                        st.markdown(f"##### {all_detail_product[index][0]}")
                        st.markdown(f"**Price:** {all_detail_product[index][1]}")
                        if all_detail_product[index][9] == None:
                            st.markdown(f"*Product Sales: Not Available*")
                        else:
                            st.markdown(f"*Product Sales: {all_detail_product[index][9]}*+ bought in the past month")
                        st.markdown(f"Weighted Combined Similarity Score(Normalized): {top_k_recommendations_dict[index]:.2f}")
                        st.markdown(f"Average Rating on Website: {all_detail_product[index][10]}")
                        st.markdown(f"Count of Total Reviews: {all_detail_product[index][11]}")
                        st.markdown(f"**Average sentiment score:** {all_detail_product[index][4]:.2f}")
                        st.markdown(f"**Overall sentiment:** {'positive' if all_detail_product[index][4] > 0 else 'negative' if all_detail_product[index][4] < 0 else 'neutral'}")
                    with st.expander("About the Product"):
                        st.write(pd.DataFrame(all_detail_product[index][3], columns=['About the Product']))
                    with st.expander("Show Top Reviews"):
                        st.dataframe(pd.DataFrame(all_detail_product[index][5], columns=['Review']))
    except Exception as e:
        print(e)

    if not os.path.isfile("all_detail_product.pkl") or os.stat("all_detail_product.pkl").st_size == 0 or not os.path.isfile("product_dict.pkl") or os.stat("product_dict.pkl").st_size == 0:
        all_detail_list_load = []
        product_dict_list_load = []
        with open("all_detail_product.pkl", "wb") as f:
            pickle.dump(all_detail_list_load, f)
        with open("product_dict.pkl", "wb") as f:
            pickle.dump(product_dict_list_load, f)
    else:
        with open("all_detail_product.pkl", "rb") as f:
            all_detail_list_load = pickle.load(f)
        with open("product_dict.pkl", "rb") as f:
            product_dict_list_load = pickle.load(f)
    
    all_detail_list_load.append(all_detail_product)
    product_dict_list_load.append(product_dict)
    with open("all_detail_product.pkl", "wb") as f:
        pickle.dump(all_detail_list_load, f)
    
    with open("product_dict.pkl", "wb") as f:
        pickle.dump(product_dict_list_load, f)

    

def get_seller_amazon_product_from_url(url):
    try:
        soup = scrape_data(url)
       
        product_details = get_product_details(soup)
        image = soup.find('img', alt = product_details['name'])
        response = requests.get(image['src'])
        print(image['src'])
        img_pil = Image.open(BytesIO(response.content))
        description = get_about_this_item(soup)

        reviews = scrape_reviews(url)
        average_compound_score = analyze_reviews(reviews)
        product_detail = [product_details['name'], " ".join(description[1]), img_pil, url]
        all_detail = [product_details['name'], product_details['price'], description[0], description[1], average_compound_score, reviews,url, image['src'], 'Amazon', product_details['bought'], product_details['average_rating'], product_details['total_reviews']]
        return product_detail, all_detail
    except Exception as e:
        print(e)
        return {}
def get_seller_flipkart_product_from_url(url):
    try:
        product_data = utils_flipkart.get_product_data(url)
        
        product = {
                        "title": product_data["title"], 
                        "price": product_data["price"], 
                        "link": product_data["link"],
                        "rating": product_data["rating"],
                        "description": product_data["description"],
                        "image_url": product_data["image_url"],
                        "reviews": product_data["reviews"],
                        "count_reviews": product_data["count_reviews"],
                        "average_rating": product_data["average_rating"]
                    }
        product_detail_flipkart, all_detail_flipkart = process_element_flipkart(product)
        print(product_detail_flipkart, all_detail_flipkart)
        return product_detail_flipkart, all_detail_flipkart
    except Exception as e:
        print(e)
        return {}
    


# rs = get_seller_amazon_product_from_url('https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX6NQMD/ref=sr_1_6?dib=eyJ2IjoiMSJ9.4Amcm6ymShwYf2cUNy6g85S9v2igxHAVZIUT04qpVS9hDPQn-fIYfKJxxKAv6p4vGhXGfOYZfq84YAK8MIW2g8EJxFNluIQneY__A6MK-7M1nz2N2K05yaOtdB8nvWdp51M03ykLJ68Xrc9DhbdTH-UO-fM49o-3SNkiT7lJ4-cddNaXTKchsVBRJEGyJfG5NqIupNzurruhSTUzCnV4rUn8hsTxnl4pAVseu1kgPeo.7onAx1xXkS85OoK7tAbo-w_SZ28xNNPgH0kAS8piTbY&dib_tag=se&keywords=Iphone+15&qid=1713882530&sr=8-6')
# print(rs)
if st.button('Find'):
    get_data(key)




