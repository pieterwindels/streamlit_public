#IMPORT THE MODULES WE NEED
import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import time
import random
import json
import pandas as pd
import numpy as np

#FUNCTION TO SCRAPE THE PRIVATE IW PHONE NRS
@st.cache(ttl=108000, show_spinner=False)
def scrape_IW_private(koop_huur, pand, df):
  
  if not df.empty:

    header_list = [{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'},
               {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}, 
               {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'},
               {'User-Agent':'Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1'},
               {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'}, 
               {'User-Agent':'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'},
               {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'}]
    contact=[]
    for item in df[df['customerName']=='PRIVATE'][['id', 'property-location-locality', 'property-location-postalCode']].iterrows():
      url='https://www.immoweb.be/nl/zoekertje/'+str(pand)+'/'+str(koop_huur)+'/'+str(item[1][1])+'/'+str(item[1][2])+'/'+str(item[1][0])
      try:
        page = requests.get(url, headers = random.choice(header_list), timeout=6)
        text=page.text
        tel_nr=text.partition('"logoUrl"')[2].partition(',"name"')[0]
        contact.append(tel_nr)
        time.sleep(random.randint(2,5))
      except Exception as e:
        df_IW_contact=pd.DataFrame({})
        return df_IW_contact
    contact_series=pd.Series(contact, name='contact')
    try:
      id_series=df[df['customerName']=='PRIVATE']['id'].reset_index()
      df_IW_contact = pd.concat([contact_series, id_series], axis=1)
      df_IW_contact.drop(columns='index', inplace=True)
      #df_IW['contact']=df['contact'].str.replace(':null,', '')
    except Exception as e:
      df_IW_contact=pd.DataFrame({})
      return df_IW_contact

    return  df_IW_contact
  
  else:
    df_IW_contact=pd.DataFrame({})
    return df_IW_contact
