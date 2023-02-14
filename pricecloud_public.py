#IMPORT THE MODULES WE NEED
import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import time
import random
import json
import pandas as pd
import numpy as np
import copy
import ssl
from email.message import EmailMessage
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import xlsxwriter
from io import BytesIO

import url_constructor
import scrape_zi
import scrape_iw
import scrape_IW_private
import df_IW_concat
import delete_columns_rows
import rename_columns
import clean_df_IW
import clean_df_ZM

scrape_zi=st.cache(scrape_zi, ttl=86400, show_spinner=False)
scrape_iw=st.cache(scrape_iw, ttl=86400, show_spinner=False)
scrape_IW_private=st.cache(scrape_IW_private, ttl=86400, show_spinner=False)

#DEFINE ALL NEEDED FUNCTIONS

#FUNCTION TO INCREMENT THE SESSION STATE
def increment_counter():
    st.session_state.count += 1
    
#FUNCTION TO RESET THE SESSION STATE
def counter_reset():
    st.session_state.count=0
  
#HERE WE START THE EXECUTION OF THE FUNCTIONS BASED ON INPUT FROM USER
#WE ASSIGN A SESSION STATE COUNTER AND PUT IN CACHE
with open('postcodes.txt', 'r') as f:
    data=f.read()
    postcodes=json.loads(data.replace("'",'"'))
if 'count' not in st.session_state:
  st.session_state.count = 0
if st.session_state.count==0:
  st.header('Welkom op de PriceCloud vastgoed app!')
  st.text('Maak een lijst van alle beschikbare panden in jouw regio!')
  #we assign a tuple with names of hoofdgemeenten to choose from
  with st.sidebar:
    with st.form('invulformulier'):
      st.header('Van welke panden wens je een up-to-date lijst?')
      pand=st.radio('Wat is het type vastgoed?', ['huis', 'appartement', 'garage', 'bedrijfsvastgoed', 'grond'], key='pand')
      hoofdgemeente=st.selectbox('In welke gemeente is het pand gelegen?', list(set(postcodes.values())), key='hoofdgemeente',
                                 help='In this trial version only a few options can be selected, in the paid version all options are visible.')
      koop_huur=st.radio('Te koop of te huur?', ['te-koop', 'te-huur'], key='koop_huur')
      st.form_submit_button(label="Geef me de lijst", on_click=increment_counter)
if st.session_state.count==1:
  st.session_state.pand=st.session_state.pand
  st.session_state.hoofdgemeente=st.session_state.hoofdgemeente
  st.session_state.koop_huur=st.session_state.koop_huur
  with st.spinner('BEZIG OM DE DATA VAN DE PANDEN TE VERZAMELEN ...'): 
    placeholder=st.empty()
    a, b= url_constructor.url_constructor(st.session_state.koop_huur, st.session_state.pand, st.session_state.hoofdgemeente)
    df_ZM_scrape=scrape_zi.scrape_zi(a)
    df_ZM=copy.deepcopy(df_ZM_scrape)
    placeholder.text('ONS OPZOEKWERK LOOPT...NOG EVEN GEDULD!')
    df_IW_scrape=scrape_iw.scrape_iw(b)
    df_IW=copy.deepcopy(df_IW_scrape)
    if df_ZM.empty and df_IW.empty:
        st.write('er zijn geen panden')
    else:
        st.dataframe(df_ZM)
        st.dataframe(df_IW
        
   '''     
        placeholder.text('WEERAL EEN STAP DICHTER...NOG EVEN GEDULD!')
        df_IW_contact_scrape=scrape_IW_private.scrape_IW_private(st.session_state.koop_huur, st.session_state.pand, df_IW)
        df_IW_contact=copy.deepcopy(df_IW_contact_scrape)
        placeholder.text('DE DATA ZIJN VERZAMELD...DEZE GAAN WE NU ANALYSEREN!')
        df_IW=df_IW_concat.df_IW_concat (df_IW, df_IW_contact)
        df_ZM, df_IW=delete_columns_rows.delete_columns_rows(df_ZM, df_IW)
        df_ZM, df_IW=rename_columns.rename_columns(df_ZM, df_IW)
        df_ZM=clean_df_ZM.clean_df_ZM(df_ZM, st.session_state.koop_huur, st.session_state.pand)
        df_IW=clean_df_IW.clean_df_IW(df_IW, st.session_state.koop_huur, st.session_state.pand)
        placeholder.text('ALLES IS KLAAR...HIER ZIJN DE GEVRAAGDE PANDEN!')
        placeholder.empty()
        #we combine the two dataframes into one:
        result_concat = pd.concat([df_ZM, df_IW], ignore_index=True, sort=False)
        #we replace values in the concatenated df:
        df_n=result_concat.astype('string')
        df_n.replace({np.nan:'geen info', None:'geen info', pd.NA:'geen info'}, inplace=True)
        #we group by values to remove the duplicates:
        g=df_n.groupby(['prijs_m2', 'prijs', 'adres']).agg(lambda x: ' '.join(x.unique())).reset_index(['prijs_m2', 'prijs', 'adres'])
        g_fin=g.groupby(['prijs_m2', 'prijs']).agg(lambda x: ' '.join(x.unique())).reset_index(['prijs_m2', 'prijs'])
        #we replace certain values:
        lt=['prijs_m2', 'prijs', 'adres', 'pand', 'gemeente','postcode', 'woonopp',
            'slaapkamers', 'prijs_verlaagd', 'energielabel','nieuwbouw', 'dagen_online',
            'adverteerder', 'perceel_opp', 'prijs_extra_kosten', 'oude_prijs', 'extra_info']
        replacers={'geen info': '', '_': ''}
        for x in lt:
          g_fin[x]=g_fin[x].str.replace('geen info', '')
        g_fin['prijs_m2']=g_fin['prijs_m2'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['prijs']=g_fin['prijs'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['woonopp']=g_fin['woonopp'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['slaapkamers']=g_fin['slaapkamers'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['dagen_online']=g_fin['dagen_online'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['perceel_opp']=g_fin['perceel_opp'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['prijs_extra_kosten']=g_fin['prijs_extra_kosten'].replace('', np.nan).astype(float, errors='ignore')
        g_fin['oude_prijs']=g_fin['oude_prijs'].replace('', np.nan).astype(float, errors='ignore')
        g_fin.round(0)
        
        st._legacy_dataframe(g_fin.style
                             .format('€{:.0f}', subset=['prijs_m2', 'prijs', 'prijs_extra_kosten', 'oude_prijs'])
                             .format('{:.0f}m²', subset=['woonopp']))
        
        #st.bar_chart(g_fin['prijs_m2'])
        
        #prepare the Excel file for download:
        output = BytesIO()
        # Write files to in-memory strings using BytesIO
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        # Convert the dataframe to an XlsxWriter Excel object.
        g_fin.to_excel(writer, sheet_name='Sheet1')
        writer.close()
        st.download_button(label="Download Excel workbook",
                           data=output.getvalue(),
                           file_name="pandas_simple.xlsx",
                           mime="application/vnd.ms-excel")
 '''
