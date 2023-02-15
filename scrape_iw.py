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
@st.cache(ttl=86400, show_spinner=False)
def scrape_iw(url_iw):
  """This function scrapes all the immoweb pages that have real estate 
  
  matching the search terms. Identical srapes are cached for 24h.
  """

  #define the scrape headers:
  header_list = [{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'},
                 {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}, 
                 {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'},
                 {'User-Agent':'Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1'},
                 {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'}, 
                 {'User-Agent':'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'},
                 {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'}]
  
  #define the empty list
  vastgoed_data = []
  
  #define the counter for scrape following pages:
  ct=2
  
  #we collect the number of pages results
  try:
    page = requests.get(url_iw, headers = random.choice(header_list), timeout=6)
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
          page = requests.get(url, headers = random.choice(header_list))
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
