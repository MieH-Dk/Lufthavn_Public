import numpy as np
import pandas as pd
from datetime import datetime, timedelta
current_date = datetime.today()


def format_hour(datetime):
    """Hjælpefunktion til at formattere tid med halvtimesintervaller"""
    hour=datetime.strftime('%H')
    minute=datetime.minute
    if minute<30:
        return f"{hour}:00-{hour}:29"
    else:
        return f"{hour}:30-{hour}:59"
day_mapping = {0: 'Mandag', 1: 'Tirsdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag', 5: 'Lørdag', 6: 'Søndag'}
month_mapping = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober',11: 'November',12: 'December'}
list_of_WB_AL = ['AI', 'AA', 'DL']

def format_df_menz(xlxs_file):
    menz_df=pd.read_excel(xlxs_file, usecols="A:J") #importer excelfil
    menz_df['ValidFromStr']=pd.to_datetime(menz_df['ValidFromStr'], dayfirst=True)
    menz_df['ValidToStr']=pd.to_datetime(menz_df['ValidToStr'], dayfirst=True)
    menz_df = menz_df[menz_df['ArrTimeStr'].notna()]
    menz_df['Flight'] = menz_df['ArrFlightPrefix'] +' '+ menz_df['ArrFlightNo'].astype(str)
    return menz_df

def create_data_for_correct_df_menz(df):
    list_of_rows=[] #this is the one to be the final df
    for ind in df.index:
        flight=df['Flight'][ind]
        from_=df['ValidFromStr'][ind]
        to=df['ValidToStr'][ind]
        frequency=[int(char)-1 for char in df['ValidDay'][ind] if char.isdigit()] #makes a list of day indices
        dest=df['ArrAirport'][ind]
        time=df['ArrTimeStr'][ind]
        aircraft = df['AircraftType'][ind]
        dates = []
        current_date=from_
        while current_date <= to:
            if current_date.weekday() in frequency:  # Monday has a weekday index of 0 and so on
                dates.append(current_date)
            current_date += timedelta(days=1)
        for day in dates:
            new_row={'Flight': flight, 'Dest':dest, 'dato':day, 'Ugedag':day.weekday(), 'tid':time, 'Flytype': aircraft}
            list_of_rows.append(new_row)
    return list_of_rows

def convert_to_utc_plus_1(df):
    df['tid'] = pd.to_datetime(df['tid'], format='%H:%M').dt.time
    df['datotid'] = df.apply(lambda row: row['dato'].replace(hour=row['tid'].hour, minute=row['tid'].minute), axis=1)
    df['datotid'] = df['datotid']+ timedelta(hours = 2)
    df['tid'] = df['datotid'].dt.time
    df['dato'] = df['datotid'].apply(lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0))
    del df['datotid']
    return df

def create_final_dataframe_menz(list_of_rows):
    parsed_df=pd.DataFrame(list_of_rows, columns=['Flight','Dest', 'dato', 'Ugedag', 'tid', 'Flytype'])
    parsed_df = convert_to_utc_plus_1(parsed_df)
    parsed_df['tids_slot']=parsed_df['tid'].apply(format_hour)
    parsed_df['Ugedag']=parsed_df['Ugedag'].map(day_mapping)
    parsed_df['uge']=parsed_df['dato'].dt.isocalendar().week
    parsed_df=parsed_df[parsed_df['dato']>=datetime(current_date.year, current_date.month, 1)].reset_index(drop=True)
    parsed_df['måned']=parsed_df['dato'].dt.month
    parsed_df['måned']=parsed_df['måned'].map(month_mapping)
    parsed_df['dato']=parsed_df['dato'].dt.date
    parsed_df['Rengøringstype'] = 'clean'
    parsed_df['AL'] = parsed_df['Flight'].apply(lambda x: x.split()[0])
    parsed_df['WB'] = parsed_df['AL'].apply(lambda x: 'False' if x not in list_of_WB_AL else 'A')
    parsed_df=parsed_df.sort_values(by=['dato', 'tid']).reset_index(drop=True)
    parsed_df['Origin_file']='Menzies'
    return parsed_df[['Flight', 'Dest', 'dato', 'uge','Ugedag', 'måned','tid', 'tids_slot', 'Rengøringstype', 'Origin_file', 'WB', 'Flytype', 'AL']]

def menzies_final_df(file_name1):
    df=format_df_menz(file_name1)
    list_data=create_data_for_correct_df_menz(df)
    parsed_df=create_final_dataframe_menz(list_data)
    return parsed_df