import streamlit as st
import factorial
num = st.number_input('Insert a number')
st.write(num)
a=factorial.fact(num)
st.write(a)
