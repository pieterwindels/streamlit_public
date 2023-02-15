#IMPORT THE MODULES WE NEED
import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import time
import random
import json
import pandas as pd
import numpy as np

#FUNCTION TO SCRAPE THE SELECTED ZM PAGES
@st.cache(ttl=108000, show_spinner=False)
def scrape_zi(url_zi):
  """This function scrapes all the zimmo pages that have real estate 
  
  matching the search terms. Output is a pandas df. Identical scrapes
  
  are cached for 24h.
  """
  #define scrape headers:
  header_list = [{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'},
               {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}, 
               {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'},
               {'User-Agent':'Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1'},
               {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'}, 
               {'User-Agent':'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'},
               {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'}]
  headers = {'User-Agent':random.choice(header_list),
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.9',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Host':'www.zimmo.be',
            'Referer':'https://www.google.com/'
            }

  #define the empty lists:
  vastgoed={'property_time':[],
          'property_code':[]}
  vastgoed_json=[]
  
  #define the counter for scrape following pages:
  ct=2
  
  #we initiate the scrape, we start with the 1st page
  #there we scrape number of page results and the url hash for other pages
  #in addition to the first page real estate data results:
  try:
    with requests.Session() as s:
      page = s.get(url_zi, headers = headers, timeout=6)
      soup=bs(page.text, 'html.parser')
      vastgoed_json.append(json.loads((page.text.split('properties: ')[1].split(',\n')[0]), strict=False))
      items=soup.find_all('div', attrs={'class':'property-item'})
      for i in items:
            if i.find('span', attrs={'class':"clock-icon property-item_icon"}):
              vastgoed['property_time'].append((i.find('span', attrs={'class':"clock-icon property-item_icon"}).get_text('/', strip=True).replace('clock/','')))
            else:
              vastgoed['property_time'].append(None) 
            if i['data-code']:
              vastgoed['property_code'].append(i['data-code'])
            else:
              vastgoed['property_code'].append(None)
      
      #define the number of page results:
      aantal_pg=soup.find("div", attrs={"class": "results"})
      aantal_pg=-(-(int((aantal_pg.get_text()).split('resultaten')[0].split('van')[1].strip()))//21)
      
      #define the page hash for all other pages than page 1, specific to zimmo site:
      url_attach=soup.find("div", attrs={'class':'dropdown-menu open'})
      url_attach=((url_attach.a['href'].split('/?search='))[1])[:-1]
      
      #scrape the real estate date from all following pages: 
      while ct<=int(aantal_pg):
        try:
          #define scrape headers:
          header_list = [{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'},
                         {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'},
                         {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'},
                         {'User-Agent':'Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1'},
                         {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'},
                         {'User-Agent':'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'},
                         {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'}]
          headers = {'User-Agent':random.choice(header_list),
                     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                     'Accept-Encoding':'gzip, deflate, br',
                     'Accept-Language':'en-US,en;q=0.9',
                     'Cache-Control':'no-cache',
                     'Connection':'keep-alive',
                     'Host':'www.zimmo.be',
                     'Referer':'https://www.google.com/'
                    }
          time.sleep(random.randint(1,4))
          url=url_zi.strip('#gallery')+'?search='+url_attach+str(ct)+'#gallery'
          page = s.get(url, headers = headers, timeout=6)
          soup=bs(page.text, 'html.parser')
          vastgoed_json.append(json.loads((page.text.split('properties: ')[1].split(',\n')[0]), strict=False))
          items=soup.find_all('div', attrs={'class':'property-item'})
          for i in items:
            if i.find('span', attrs={'class':"clock-icon property-item_icon"}):
              vastgoed['property_time'].append((i.find('span', attrs={'class':"clock-icon property-item_icon"}).get_text('/', strip=True).replace('clock/','')))
            else:
              vastgoed['property_time'].append(None) 
            if i['data-code']:
              vastgoed['property_code'].append(i['data-code'])
            else:
              vastgoed['property_code'].append(None)
          ct=ct+1
          if (ct==8 or ct==15 or ct==23 or ct==32 or ct==42):
            time.sleep(5) 
        except Exception as e:
          df_ZM=pd.DataFrame({})
          return df_ZM
  except Exception as e:
    df_ZM=pd.DataFrame({})
    return df_ZM

  #combine the different data sets into one single list of dicts. Each dict represents all values for a property.
  vastgoed_data_ZM=[]
  for item in vastgoed_json:
    for dictionary in item:
      vastgoed_data_ZM.append(dictionary)
  e={}
  x=0
  for i in vastgoed["property_code"]:
      e[i]=vastgoed["property_time"][x]
      x=x+1
  for item in vastgoed_data_ZM:
    for key in e:
      if item["code"]==key:
        item['tijd_sinds_publ']=e[key]
      else:
        continue 
  df_ZM=pd.json_normalize(vastgoed_data_ZM, sep='-')
  return df_ZM
