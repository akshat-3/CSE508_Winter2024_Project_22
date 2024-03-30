
import streamlit as st
from flipkart_final import get_data
st.markdown('### Group 22 IR Project')
st.markdown('#### E-Commerce Competitive Analysis System')
st.markdown('Search for a product on Flipkart')
key = st.text_input('Enter the product name')

if st.button('Find'):
    st.write(get_data(key))


