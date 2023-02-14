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
