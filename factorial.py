import streamlit as st
import time
@st.cache(ttl=5)
def fact(num):
  i=0
  while i<num:
    time.sleep(1)
    i=i+1
  return 'ten einde'
