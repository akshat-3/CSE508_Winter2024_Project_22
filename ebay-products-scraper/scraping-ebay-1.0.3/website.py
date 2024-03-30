
import streamlit as st
import os
import pandas as pd

st.markdown('### Group 22 IR Project')
st.markdown('#### E-Commerce Competitive Analysis System')
st.markdown('Search for a product on EBay')
key = st.text_input('Enter the product name')

command = f"scrapy crawl ebay -o output.csv -a search='{key}' -a pages=1"

if st.button('Find'):
    st.write("This may take a while, please wait...")
    os.system(command)
    df = pd.read_csv('output.csv')
    st.write(df)



