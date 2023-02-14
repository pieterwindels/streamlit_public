#FUNCTION TO SCRAPE THE PRIVATE IW PHONE NRS

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
