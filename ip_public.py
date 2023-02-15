import requests
import streamlit as st
URL='http://httpbin.org/ip'
page=requests.get(URL)
st.write(page.text)
