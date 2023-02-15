import streamlit as st
def fact(num)
  
factorial = 1    
if num < 0:    
   return " Factorial does not exist for negative numbers"    
elif num == 0:    
   return "the factorial of 0 is 1"
else:    
   for i in range(1,num + 1):    
       factorial = factorial*i    
   return f"The factorial of {num} is {factorial}"    
