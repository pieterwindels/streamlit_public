import streamlit as st
num = st.number_input('Insert a number')
a=fact(num)
st.write(a)
