import numpy as np
import pandas as pd
from datetime import datetime, timedelta
current_date = datetime.today()
from pathlib import Path
BASE_DIR = Path(__file__).parent

wr_file = BASE_DIR / "SGH datafiler" / "SK wasteremoval_januar24.xlsx"

wr_df = pd.read_excel(wr_file, sheet_name="Filtreret")

#wr_file='Selskaber\SGH\SGH datafiler\SK wasteremoval_januar24.xlsx'

def format_hour(datetime):
    """Hjælpefunktion til at formattere tid med halvtimesintervaller"""
    hour=datetime.strftime('%H')
    minute=datetime.minute
    if minute<30:
        return f"{hour}:00-{hour}:29"
    else:
        return f"{hour}:30-{hour}:59"
    
def create_rengoringstype(row, wr_list):
    if row['AL'] == 'SK' and row['Dest'] in wr_list:
        return 'wr'
    else:
        return 'clean'
    
    # Lister med sorteringskriterier
airlines_to_remove=['SQ', 'TG', '6I', 'BJ', 'BT', 'D0', 'DX', 'ET', 'EW', 'JTD', 'PE', 'R6', 'SLD', 'V7', 'WF', 'TF', 'YW', 'ZQ'] #AL
waste_remove=list(wr_df['STN'])
#waste_remove=['HAU', 'KRS', 'MMX', 'SVG', 'TRD', 'LLA' 'UME', 'TOS', 'BOO', 'OSL', 'ARN', 'AAL', 'AAR', 'AES', 'BGO', 'FAE', 'GOT'] #dest
wide_body=['333', '330', '32Q', '359', '788', '338', '332', '767', '76W', '789', '339', '76W'] #Note here that '32Q' is just normal clean, if AL=='DK'
day_mapping_SGH = {1: 'Mandag', 2: 'Tirsdag', 3: 'Onsdag', 4: 'Torsdag', 5: 'Fredag', 6: 'Lørdag', 7: 'Søndag'}
month_mapping = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober',11: 'November',12: 'December'}


def format_SGH(SGHFile):
    """Returns """
    fly_df_all=pd.read_excel(SGHFile, skiprows=0, header=0) #importer excelfil
    fly_df_all=fly_df_all[~fly_df_all['AL'].isin(airlines_to_remove)] #fjerner airlines som ikke hører til os
    #De næste linjer er for at konvertere dato og tid til rigtig format
    fly_df_all['ym'] = fly_df_all['ym'].astype(str).str[:4] + '-' + fly_df_all['ym'].astype(str).str[-2:] 
    fly_df_all['d'] = fly_df_all['d'].astype(str).str.zfill(2)
    fly_df_all['dato'] = fly_df_all['d'] + '-' + fly_df_all['ym']
    fly_df_all['dato']=pd.to_datetime(fly_df_all['dato'], format='%d-%Y-%m') #dato er nu på format yyyy-mm-dd
    fly_df_all['måned']=fly_df_all['dato'].dt.month #månedskolonne
    fly_df_all['måned']=fly_df_all['måned'].map(month_mapping) #måneder nu på dansk
    fly_df_all=fly_df_all[fly_df_all['dato']>=datetime(current_date.year, current_date.month, 1)].reset_index(drop=True) #fjerner data fra før den første i nuværende måned
    fly_df_all['tid']= fly_df_all['Tid'].astype(str).str.zfill(4) #klokkeslæt som string
    fly_df_all['tid'] = pd.to_datetime(fly_df_all['tid'], format='%H%M').dt.time #klokkeslæt nu som datetime
    fly_df_all['uge']= fly_df_all['dato'].dt.isocalendar().week #ugenummer
    fly_df_all['dato']=fly_df_all['dato'].dt.date #dato
    fly_df_all['Ugedag']=fly_df_all['Ugedag'].map(day_mapping_SGH) #ugedag 
    fly_df_all['WB']=fly_df_all['Flytype'].isin(wide_body) #boolean column.
    mask = ((fly_df_all['WB'] == True) & (fly_df_all['AL'] == 'DK') & (fly_df_all['Flytype'] == '32Q')) | ((fly_df_all['WB'] == True) & (fly_df_all['AL'] == 'TP')) # '32Q' is just normal clean, if AL=='DK'
    fly_df_all.loc[mask, 'WB'] = False
    fly_df_all['WB'] = fly_df_all['WB'].apply(lambda x: 'True' if x else 'False')
    mask_a = ((fly_df_all['WB'] == 'True') & (fly_df_all['Fase'] == 'A'))
    mask_d = ((fly_df_all['WB'] == 'True') & (fly_df_all['Fase'] == 'D'))
    fly_df_all.loc[mask_a, 'WB'] = 'A'
    fly_df_all.loc[mask_d, 'WB'] = 'D'
    fly_df_all['Flight']=fly_df_all['AL']+' '+fly_df_all['Flight'].astype(str)
    fly_df_all['Rengøringstype'] = fly_df_all.apply(create_rengoringstype, wr_list=waste_remove, axis=1)
    fly_df_all['tids_slot']=fly_df_all['tid'].apply(format_hour)
    arrival_mask = ((fly_df_all['Fase'] == 'A') | (fly_df_all['WB'] != 'False')) #this is maybe superfluous
    fly_df_all = fly_df_all.loc[arrival_mask]#this is maybe superfluous
    mask_to_delete = ((fly_df_all['WB'] == 'D') & (fly_df_all['AL'] == 'SK') & (fly_df_all['Flytype'] == '32Q')) & (fly_df_all['Dest'] == 'OSL')| ((fly_df_all['WB'] == 'D') & (fly_df_all['AL'] == 'SK') & (fly_df_all['Flytype'] == '333')) & (fly_df_all['Dest'].isin(['ARN', 'OSL']))#special case. These WB's should only have arrival, and arrival should be clean instead of wr
    mask_to_change = ((fly_df_all['WB'] == 'A') & (fly_df_all['AL'] == 'SK') & (fly_df_all['Flytype'] == '32Q')) & (fly_df_all['Dest'] == 'OSL')| ((fly_df_all['WB'] == 'A') & (fly_df_all['AL'] == 'SK') & (fly_df_all['Flytype'] == '333')) & (fly_df_all['Dest'].isin(['ARN', 'OSL']))
    fly_df_all.loc[mask_to_change, 'Rengøringstype'] = 'clean'
    fly_df_all = fly_df_all[~mask_to_delete]
    fly_df_all['Origin_file'] = 'SGH'
    fly_df_all=fly_df_all.sort_values(by=['dato', 'tid'])
    return fly_df_all[['Flight', 'Dest', 'dato', 'uge','Ugedag', 'måned','tid', 'tids_slot', 'Rengøringstype', 'Origin_file','WB', 'Flytype', 'AL']]
