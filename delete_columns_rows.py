import pandas as pd
import numpy as np

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
