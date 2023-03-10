#IMPORT THE MODULES WE NEED
import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import time
import random
import json
import pandas as pd
import numpy as np

#FUNCTION TO SCRAPE THE SELECTED IW PAGES
@st.cache_data(ttl=86400, show_spinner=False)
def scrape_iw(url_iw):
  """This function scrapes all the immoweb pages that have real estate 
  
  matching the search terms. Identical srapes are cached for 24h.
  """

  #define the scrape headers:
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
  
  #define the empty list
  vastgoed_data = []
  
  #define the counter for scrape following pages:
  ct=2
  
  #we collect the number of pages results
  try:
    page = requests.get(url_iw, headers = headers, timeout=6)
    text=page.text
    #we collect the number of pages results
    aantal_pg=text.partition(":result-count='")[2].partition("'")[0]
    if int(aantal_pg)==0:
      df_IW=pd.DataFrame({})
      return df_IW
    else:
      aantal_pg=-(-(int(aantal_pg))//30)
      #we collect the webpage 1 we want to scrape
      a=text.partition(":results='")[2].partition(":results-storage='")[0].rstrip()
      b=a.replace('&quot;','"').replace("[]", "null").rstrip("'")
      vastgoed_data_json=json.loads(b, strict=False)
      vastgoed_data.append(vastgoed_data_json)
      #we collect all the following pages
      while ct<=int(aantal_pg):
        try:
          time.sleep(random.randint(1,4))
          url=url_iw.replace('1&orderBy=relevance', str(ct)+'&orderBy=relevance')
          page = requests.get(url, headers = headers)
          text=page.text
          a=text.partition(":results='")[2].partition(":results-storage='")[0].rstrip()
          b=a.replace('&quot;','"').replace("[]", "null").rstrip("'")
          vastgoed_data_json=json.loads(b, strict=False)
          vastgoed_data.append(vastgoed_data_json)
          ct=ct+1
          if (ct==8 or ct==15 or ct==23 or ct==32 or ct==42):
              time.sleep(5) 
        except Exception as e:
          df_IW=pd.DataFrame({})
          return df_IW
  except Exception as e:
    df_IW=pd.DataFrame({})
    return df_IW
  #combine the different data sets into one single list of dicts. Each dict represents all values for a property.
  if vastgoed_data:
    vastgoed_data_IW=[]
    for item in vastgoed_data:
      for dictionary in item:
        vastgoed_data_IW.append(dictionary)
    df_IW=pd.json_normalize(vastgoed_data_IW, sep='-')
    return df_IW
  else:
    df_IW=pd.DataFrame({})
    return df_IW  
