import streamlit as st
import factorial
num = st.number_input('Insert a number')
a=factorial.fact(num)
st.write(a)
