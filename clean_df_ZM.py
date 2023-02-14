import pandas as pd
import numpy as np
import json

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
