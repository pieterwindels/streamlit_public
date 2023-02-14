
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
  
