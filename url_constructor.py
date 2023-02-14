#FUNCTION TO CONSTRUCT SEARCH URL

def url_constructor (koop_huur, pand, hoofdgemeente):

  #define the URL part to reflect the pand type:

  if pand=='bedrijfsvastgoed':
    pand_zi, pand_iw=pand,'handelszaak'
  else:
    pand_zi, pand_iw=pand, pand

  #define the URL part (as string) to reflect the hoofdgemeente (we use the postcodes dictionary):

  hoofdgemeente_iw=''.join([k+',' for k,v in postcodes.items() if v==hoofdgemeente]).strip(',')
  
  #construct the full length URL:

  url_zi='https://www.zimmo.be/nl/'+hoofdgemeente+'/'+koop_huur+'/'+pand_zi+'/#gallery'
  url_iw='https://www.immoweb.be/nl/zoeken/'+pand_iw+'/'+koop_huur+'?countries=BE&postalCodes='+hoofdgemeente_iw+'&page=1&orderBy=relevance'
  
  return url_zi, url_iw
