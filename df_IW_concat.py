#FUNCTION TO COMBINE THE SCRAPED IW PROPERTIES AND SCRAPED PRIVATE PHONE NRS
def df_IW_concat (df_IW, df_IW_contact):
  try:
    df_IW=pd.merge(df_IW, df_IW_contact, how='outer', on='id')
  except Exception as e:
    df_IW=pd.DataFrame({})
    return df_IW
    
  return df_IW
