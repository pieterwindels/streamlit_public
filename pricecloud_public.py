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


#DEFINE ALL NEEDED FUNCTIONS

#FUNCTION TO INCREMENT THE SESSION STATE
def increment_counter():
    st.session_state.count += 1
    
#FUNCTION TO RESET THE SESSION STATE
def counter_reset():
    st.session_state.count=0
    

#FUNCTION TO SCRAPE THE SELECTED IW PAGES
@st.cache(ttl=86400, show_spinner=False)
def scrape_iw(url_iw):
  """This function scrapes all the immoweb pages that have real estate 
  
  matching the search terms. Identical srapes are cached for 24h.
  """

  #define the scrape headers:
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'}
  
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
    aantal_pg=-(-(int(aantal_pg))//30)
    #we collect the webpage 1 we want to scrape
    a=text.partition(":results='")[2].partition(":results-storage='")[0].rstrip()
    b=a.replace('&quot;','"').replace("[]", "null").rstrip("'")
    vastgoed_data_json=json.loads(b, strict=False)
    vastgoed_data.append(vastgoed_data_json)
    #we collect all the following pages
    while ct<=int(aantal_pg):
      try:
        time.sleep(random.randint(2,5))
        url=url_iw.replace('1&orderBy=relevance', str(ct)+'&orderBy=relevance')
        page = requests.get(url, headers = headers)
        text=page.text
        a=text.partition(":results='")[2].partition(":results-storage='")[0].rstrip()
        b=a.replace('&quot;','"').replace("[]", "null").rstrip("'")
        vastgoed_data_json=json.loads(b, strict=False)
        vastgoed_data.append(vastgoed_data_json)
        ct=ct+1
        if (ct==8 or ct==15 or ct==23 or ct==32):
            time.sleep(10) 
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

#FUNCTION TO SCRAPE THE PRIVATE IW PHONE NRS
@st.cache(ttl=86400, show_spinner=False)
def scrape_IW_private(koop_huur, pand, df):

  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'}
  contact=[]
  for item in df[df['customerName']=='PRIVATE'][['id', 'property-location-locality', 'property-location-postalCode']].iterrows():
    url='https://www.immoweb.be/nl/zoekertje/'+str(pand)+'/'+str(koop_huur)+'/'+str(item[1][1])+'/'+str(item[1][2])+'/'+str(item[1][0])
    try:
      page = requests.get(url, headers = headers, timeout=6)
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

#FUNCTION TO COMBINE THE SCRAPED IW PROPERTIES AND SCRAPED PRIVATE PHONE NRS
def df_IW_concat (df_IW, df_IW_contact):
  try:
    df_IW=pd.merge(df_IW, df_IW_contact, how='outer', on='id')
  except Exception as e:
    df_IW=pd.DataFrame({})
    return df_IW
    
  return df_IW

#FUNCTION TO DELETE COLUMNS NOT NEEDED IN SCRAPED DFS
def delete_columns_rows(df_ZM, df_IW):
  
  """This function takes as input the scraped df's and
  
  deletes the colums (inplace=True) that are not needed. Returns df_ZM and df_IW.
  """

  #define the columns list for each of the df's that need to be deleted:
  del_zi=['type', 'status', 'code', 'uuid', 'type_id', 'toegevoegd', 'plus',
       'status_id', 'hoofdFoto', 'zprijs', 'parcel_id', 'logo', 'proj_id',
       'favoriet', 'archief',
       'a_beschrijf', 'fotoAmount', 'isPromoted', 'subtype_naam', 
       'zimmo_kantoor_id', 'plus', 'energyWaarde', 'energyCode', 'energyLabelCategory', 'html', 
       'propertyItemLogo',
       'province', 'isPublished', 'url', 'pand_url',  
       'advertiser-phone', 'advertiser-mobile',
       'advertiser-showEmail', 'advertiser-officeType',
       'advertiser-useZimmoDetail', 'advertiser-pictureZoomPercentage',
       'advertiser-pictureLogoPosition', 'advertiser-pictureApplyMainOnly',
       'advertiser-officebox', 'advertiser-officebox_url',
       'advertiser-logo', 'advertiser-website',
       'advertiser-postalCode', 'advertiser-city', 'advertiser-address',
       'advertiser-forRent', 'advertiser-forSale',
       'advertiser-officebox_tekoop', 'advertiser-officebox_tehuur', 'percentageVerkocht',
       'shouldHidePercentageSold']
  del_iw=['id', 'customerLogoUrl', 'priceType', 'isBookmarked',
       'has360Tour', 'hasVirtualTour', 'advertisementId', 'cluster-projectInfo',
       'flags-percentSold', 'media-pictures',
       'property-subtype', 'property-title',
       'property-location-country',
       'property-location-region', 'property-location-province',
       'property-location-district', 'property-location-box',
       'property-location-propertyName', 'property-location-floor',
       'property-location-distance', 'property-location-approximated',
       'property-location-regionCode', 'property-location-type',
       'property-location-hasSeaView', 'property-location-pointsOfInterest',
       'property-location-placeName', 'property-roomCount', 'publication-publisherId',
       'publication-visualisationOption', 'publication-size',
       'transaction-certificateLogoUrl', 'transaction-certificate',
       'transaction-type','transaction-rental-monthlyRentalPrice',
       'transaction-rental-monthlyRentalCosts', 'transaction-rental-yearlyRentalPrice',
       'transaction-rental-yearlyRentalPricePerSqm', 'transaction-sale-lifeAnnuity',
       'transaction-sale-hasStartingPrice', 'transaction-sale-oldPrice', 'transaction-sale-price',
       'transaction-sale-pricePerSqm', 'transaction-sale-publicSale', 'transaction-sale-toBuild',
       'transaction-sale-isSubjectToVat',
       'price-type', 'price-minRangeValue',
       'price-maxRangeValue', 'price-mainDisplayPrice',
       'price-HTMLDisplayPrice', 'price-alternativeDisplayPrice',
       'price-oldDisplayPrice', 'price-shortDisplayPrice',
       'price-accessibilityPrice', 'price-label', 'price-date',
       'price-language','price-alternativeValue', 'cluster-maxPrice', 'cluster-maxRoom', 'cluster-maxSurface',
       'cluster-bedroomRange', 'cluster-surfaceRange', 'transaction-sale-publicSale-hasPendingOverbidRight',
       'transaction-sale-publicSale-lastSessionReachedPrice', 'transaction-sale-publicSale-date',
       'cluster-projectInfo-constructor', 'cluster-projectInfo-groupId', 'cluster-projectInfo-phase',
       'cluster-projectInfo-projectName', 'cluster-projectInfo-deliveryDate', 'cluster-projectInfo-soldPercentage',
       'cluster-projectInfo-unitsDisplayMode', 'property-type', 'transaction-rental', 'transaction-sale-publicSale-status',
       'transaction-sale-publicSale-pendingOverbidAmount', 'transaction-sale-publicSale-hasUniqueSession', 'transaction-sale-publicSale-isForcedSale']
    
  #delete the columns selected and create new df's_n
  if not df_ZM.empty:

    df_ZM.drop(columns=del_zi, errors='ignore', inplace=True)
    replace_zi={'':np.nan, None:np.nan}
    df_ZM.replace(replace_zi, regex=True, inplace=True)
    

  if not df_IW.empty:

    df_IW.drop(columns=del_iw, errors='ignore', inplace=True)
    replace_iw={None:np.nan} 
    df_IW.replace(replace_iw, regex=True, inplace=True)

  return df_ZM, df_IW

#FUNCTION TO RENAME THE COLUMNS IN SCRAPED DFS
def rename_columns(df_ZM, df_IW):
  
  #define the dict listing all the columns that need to be renamed:

  rename_zi={'particulier_pand_id':'immo_privaat_zimmo', 'b_woonopp':'woonopp', 'address':'adres',
             'energyLabel':'energielabel', 'advertiser-name':'adverteerder', 'sticker':'extra_info',
             'price_drop_date':'prijs_verlaagd', 'tijd_sinds_publ':'dagen_online'}
  rename_iw={'customerName':'adverteerder', 'property-bedroomCount':'slaapkamers', 
             'property-location-locality':'gemeente',
             'property-location-postalCode':'postcode', 'property-location-street':'adres',
             'property-location-number':'huisnr', 'property-location-latitude':'lat',
             'property-location-longitude':'lon', 'property-netHabitableSurface':'woonopp',
             'property-landSurface':'perceel_opp', 'price-mainValue':'prijs', 
             'price-additionalValue':'prijs_extra_kosten', 'price-oldValue':'oude_prijs'}

  
  if not df_ZM.empty:
    df_ZM.rename(columns=rename_zi, inplace=True)
  if not df_IW.empty:
    df_IW.rename(columns=rename_iw, inplace=True)
  
  return df_ZM, df_IW

#FUNCTION TO CLEAN THE DATA IN THE ZM DF
def clean_df_ZM(df_ZM, koop_huur, pand):

  if not df_ZM.empty:
    for x in ['immo_privaat_zimmo', 'nieuwbouw', 'adres', 'gemeente', 'extra_info',
         'prijs_verlaagd', 'energielabel', 'dagen_online', 'adverteerder',
         'advertiser-name_prefix']:
         df_ZM[x] = df_ZM[x].replace([np.nan], '')

    for x in ['woonopp', 'prijs']:
         df_ZM[x] = df_ZM[x].str.replace('.', '')
         df_ZM[x] = df_ZM[x].str.replace(',', '.')
    
    df_ZM['nieuwbouw'].replace({'0':'bestaand', '1':'nieuwbouw'}, inplace=True)
  
    df_ZM['advertiser-name_prefix']=df_ZM['advertiser-name_prefix'].str.replace('Geass. notarissen ', 'Notaris')
    df_ZM['dagen_online']=df_ZM['dagen_online'].apply(lambda x: '1' if 'u' in x else x)
    df_ZM['dagen_online']=df_ZM['dagen_online'].str.replace('d', '')
  
    #df_ZM['adverteerder']=df_ZM['immo_privaat_zimmo']+'_'+df_ZM['adverteerder']+'_'+df_ZM['advertiser-name_prefix']
    df_ZM['adverteerder']=df_ZM['immo_privaat_zimmo']+df_ZM['adverteerder']+df_ZM['advertiser-name_prefix']
    df_ZM.drop(columns=['immo_privaat_zimmo','advertiser-name_prefix'], errors='ignore', inplace=True)

    df_ZM['extra_info']=df_ZM['extra_info'].replace(['new'], '')
    df_ZM['prijs_verlaagd']=df_ZM['prijs_verlaagd']+'_'+df_ZM['extra_info']
    df_ZM.drop(columns=['extra_info'], errors='ignore', inplace=True)

    dtypes_zi={'woonopp':float, 'slaapkamers':int, 'prijs':float, 'postcode':int,
             'lat':float, 'lon':float}

    df_ZM=df_ZM.astype(dtypes_zi, errors='ignore')

    df_ZM['pand']=koop_huur+' '+pand

    #flatten the propertyList dict in the column and add prijs/woonopp to correct column:
    if 'propertyList' in df_ZM.columns:
      df_ZM['prijs_proj']=[pd.json_normalize(x)['prijs_min'] if x is not np.nan else x is np.nan for x in df_ZM['propertyList']]
      df_ZM['woonopp_proj']=[pd.json_normalize(x)['woon_oppervlakte_vanaf'] if x is not np.nan else x is np.nan for x in df_ZM['propertyList']]

      df_ZM['prijs']=df_ZM[['prijs', 'prijs_proj']].min(numeric_only=True, axis=1)
      df_ZM['woonopp']=df_ZM[['woonopp', 'woonopp_proj']].min(numeric_only=True, axis=1)
      df_ZM.drop(columns=['prijs_proj','woonopp_proj', 'propertyList'], errors='ignore', inplace=True)
    
    
    df_ZM.dropna(subset=['prijs'])
    df_ZM.drop(df_ZM[df_ZM['prijs']==''].index, inplace=True)
    df_ZM.drop(df_ZM[df_ZM['prijs']=='0'].index, inplace=True)
    df_ZM.drop(df_ZM[df_ZM['prijs']==0].index, inplace=True)


    #add a column prijs_m2 where possible and first ensure values are numeric:
    df_ZM['prijs_m2']=round(df_ZM['prijs']/df_ZM['woonopp'], 1)

    
    #select the final columns for display and order them:
    df_ZM=df_ZM[['pand','gemeente','postcode','adres','prijs','woonopp',
                       'prijs_m2','slaapkamers', 'prijs_verlaagd','energielabel',
                       'nieuwbouw','dagen_online','adverteerder']]

    return df_ZM
  else:
    return df_ZM
  
#FUNCTION TO CLEAN THE DATA IN THE IW DF  
def clean_df_IW(df_IW, koop_huur, pand):

  if not df_IW.empty:
    for x in ['adverteerder', 'flags-main', 'flags-secondary', 'gemeente', 'adres',
              'huisnr', 'contact']:
       df_IW[x] = df_IW[x].replace([np.nan], '')
    
    df_IW['huisnr']=df_IW['huisnr'].str.replace(',', '')
    df_IW['contact'].replace({':null,':''}, regex=True, inplace=True)
    df_IW['flags-main']=df_IW['flags-main'].str.replace('new_construction','nieuwbouw')
    df_IW['flags-secondary']=df_IW['flags-secondary'].str.replace('new_real_estate_project', 'nieuwbouw')
    df_IW['flags-secondary']=df_IW['flags-secondary'].str.replace(', percent_sold', '')
    df_IW['adverteerder']=df_IW['adverteerder'].str.replace('PRIVATE', 'Eigenaar')

    dtypes_iw={'postcode':int, 'perceel_opp':float, 'prijs':float,
             'prijs_extra_kosten':float, 'oude_prijs':float, 'cluster-minPrice':float,
             'cluster-minSurface':float, 'slaapkamers':int, 'cluster-minRoom':int}
    df_IW=df_IW.astype(dtypes_iw, errors='ignore')

    df_IW['pand']=koop_huur+' '+pand
  
    #combine the columns for prijs, woonopp and slaapkamers for nieuwbouw en andere: 
    df_IW['prijs_f']=df_IW['cluster-minPrice'].combine_first(df_IW['prijs'])
    df_IW.drop(columns=['cluster-minPrice', 'prijs'], errors='ignore', inplace=True)
    df_IW['prijs']=df_IW['prijs_f']

    df_IW['woonopp_f']=df_IW['cluster-minSurface'].combine_first(df_IW['woonopp'])
    df_IW.drop(columns=['cluster-minSurface', 'woonopp'], errors='ignore', inplace=True)
    df_IW['woonopp']=df_IW['woonopp_f']

    df_IW['slaapkamers_f']=df_IW['cluster-minRoom'].combine_first(df_IW['slaapkamers'])
    df_IW.drop(columns=['cluster-minRoom', 'slaapkamers'], errors='ignore', inplace=True)
    df_IW['slaapkamers']=df_IW['slaapkamers_f']

    df_IW.drop(columns=['prijs_f', 'woonopp_f', 'slaapkamers_f'], errors='ignore', inplace=True)

    df_IW['adres']=df_IW['adres']+' '+df_IW['huisnr']
    df_IW.drop(columns=['huisnr'], errors='ignore', inplace=True)

    df_IW['extra_info']=df_IW['flags-main']+' '+df_IW['flags-secondary']
    df_IW.drop(columns=['flags-main', 'flags-secondary'], errors='ignore', inplace=True)

    df_IW['adverteerder']=df_IW['adverteerder']+' '+df_IW['contact']
    df_IW.drop(columns=['contact'], errors='ignore', inplace=True)

    #delete the rows where the value for 'prijs' is 0, nan, '':
    df_IW.dropna(subset=['prijs'])
    df_IW.drop(df_IW[df_IW['prijs']==''].index, inplace=True)
    df_IW.drop(df_IW[df_IW['prijs']=='0'].index, inplace=True)
    df_IW.drop(df_IW[df_IW['prijs']==0].index, inplace=True)
    
    #add a column prijs_m2 where possible and first ensure values are numeric:
    df_IW['prijs_m2']=round(df_IW['prijs']/df_IW['woonopp'], 1)


    #select the final columns for display and order them:
    df_IW = df_IW[['pand', 'gemeente','postcode','adres','prijs','woonopp',
                   'prijs_m2','slaapkamers','perceel_opp','prijs_extra_kosten',
                   'oude_prijs','adverteerder','extra_info']]

    return df_IW
  else:
    return df_IW
  
#HERE WE START THE EXECUTION OF THE FUNCTIONS BASED ON INPUT FROM USER
#WE ASSIGN A SESSION STATE COUNTER AND PUT IN CACHE
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
    a, b= url_constructor(st.session_state.koop_huur, st.session_state.pand, st.session_state.hoofdgemeente)
    df_ZM_scrape=scrape_zi(a)
    df_ZM=copy.deepcopy(df_ZM_scrape)
    placeholder.text('ONS OPZOEKWERK LOOPT...NOG EVEN GEDULD!')
    df_IW_scrape=scrape_iw(b)
    df_IW=copy.deepcopy(df_IW_scrape)
    placeholder.text('WEERAL EEN STAP DICHTER...NOG EVEN GEDULD!')
    df_IW_contact_scrape=scrape_IW_private(st.session_state.koop_huur, st.session_state.pand, df_IW)
    df_IW_contact=copy.deepcopy(df_IW_contact_scrape)
    placeholder.text('DE DATA ZIJN VERZAMELD...DEZE GAAN WE NU ANALYSEREN!')
    df_IW=df_IW_concat (df_IW, df_IW_contact)
    df_ZM, df_IW=delete_columns_rows(df_ZM, df_IW)
    df_ZM, df_IW=rename_columns(df_ZM, df_IW)
    df_ZM=clean_df_ZM(df_ZM, st.session_state.koop_huur, st.session_state.pand)
    df_IW=clean_df_IW(df_IW, st.session_state.koop_huur, st.session_state.pand)
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
    #g_fin.style.format('{:.0f}')
    st.dataframe(g_fin, use_container_width=True)
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
