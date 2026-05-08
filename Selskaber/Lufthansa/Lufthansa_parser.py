import numpy as np
import pandas as pd
from datetime import datetime, timedelta
current_date = datetime.today()

list_of_valid_flt=['CPH FRA', 'CPH MUC', 'CPH VIE', 'CPH ZRH']
day_mapping = {0: 'Mandag', 1: 'Tirsdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag', 5: 'Lørdag', 6: 'Søndag'}
month_mapping = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober',11: 'November',12: 'December'}

def format_hour(datetime):
    """Hjælpefunktion til at formattere tid med halvtimesintervaller"""
    hour=datetime.strftime('%H')
    minute=datetime.minute
    if minute<30:
        return f"{hour}:00-{hour}:29"
    else:
        return f"{hour}:30-{hour}:59"
    

def format_df_LH(xlxs_file):
    LH_df=pd.read_excel(xlxs_file, skiprows=2, header=0) #importer excelfil
    LH_df=LH_df.drop([0,1])#fjerner to øverse rækker, som ikke indeholder noget
    LH_df=LH_df[LH_df['ARR']=='CPH'].reset_index(drop=True)
    LH_df=LH_df[LH_df['Flt CITY-'].isin(list_of_valid_flt)].reset_index(drop=True)
    del LH_df['Flt CC-']
    del LH_df['Leg']
    del LH_df['ARR']
    return LH_df
def create_data_for_correct_df_LH(df):
    list_for_final_df=[]
    for index, row in df.iterrows(): 
        temp_row_list=[]
        for column, value in row.items():
            if isinstance(column, datetime): #if the column is a date
                if not pd.isna(value):#isinstance(value, None):
                    temp_row_list.append([column,value])
        for date_type in temp_row_list: #have to go through all dates from the specific row
            row_dict={}
            for column, value in row.iloc[:10].items(): #for each date i need to find all
                #print(column, value)
                row_dict[column]=value
                row_dict['dato']=date_type[0]
                row_dict['AC']=date_type[1]
            list_for_final_df.append(row_dict)
    return list_for_final_df
def create_final_dataframe_LH(list_of_rows):
    parsed_df=pd.DataFrame(list_of_rows, columns=['Flt CITY-','dato', 'AC', 'AL', 'FNR', 'DEP', 'STD', 'STA', 'Block-', 'Code', 'I/K', 'H/D'])
    del parsed_df['Flt CITY-']
    del parsed_df['STD']
    del parsed_df['Block-']
    del parsed_df['Code']
    del parsed_df['I/K']
    del parsed_df['H/D']
    parsed_df['tids_slot']=parsed_df['STA'].apply(format_hour)
    parsed_df['Ugedag']=parsed_df['dato'].dt.dayofweek
    parsed_df['Ugedag']=parsed_df['Ugedag'].map(day_mapping)
    parsed_df['uge']=parsed_df['dato'].dt.isocalendar().week
    parsed_df=parsed_df[parsed_df['dato']>=datetime(current_date.year, current_date.month, 1)].reset_index(drop=True)
    parsed_df['måned']=parsed_df['dato'].dt.month
    parsed_df['måned']=parsed_df['måned'].map(month_mapping)
    parsed_df['dato']=parsed_df['dato'].dt.date
    parsed_df['Rengøringstype'] = 'clean'
    parsed_df['Flight']=parsed_df['AL']+' '+parsed_df['FNR'].astype(str)
    del parsed_df['FNR']
    parsed_df=parsed_df.rename(columns={'DEP': 'Dest', 'STA': 'tid', 'AC': 'Flytype'})
    parsed_df['WB'] = 'False'
    parsed_df['Origin_file']='Lufthansa'
    parsed_df['Flytype'] = parsed_df['Flytype'].astype(str)
    parsed_df=parsed_df.sort_values(by=['dato', 'tid'])
    parsed_df.reset_index(drop=True, inplace=True)
    return parsed_df[['Flight', 'Dest', 'dato', 'uge','Ugedag', 'måned','tid', 'tids_slot', 'Rengøringstype', 'Origin_file', 'WB', 'Flytype', 'AL']]
def lufthansa_final_df(file_name1, file_name2=None):
    df = format_df_LH(file_name1)
    list_data = create_data_for_correct_df_LH(df)
    parsed_df = create_final_dataframe_LH(list_data)

    # If no second file is provided, just return the first parsed dataframe
    if file_name2 is None:
        return parsed_df.reset_index(drop=True)

    # Process second file
    df2 = format_df_LH(file_name2)
    list_data2 = create_data_for_correct_df_LH(df2)
    parsed_df2 = create_final_dataframe_LH(list_data2)

    # Ensure each day only comes from one dataframe (avoid duplicates)
    last_date_df1 = parsed_df['dato'].max()
    last_date_df2 = parsed_df2['dato'].max()

    if last_date_df1 >= last_date_df2:
        master_df = parsed_df
        non_master_df = parsed_df2
    else:
        master_df = parsed_df2
        non_master_df = parsed_df

    master_dates = master_df['dato']
    non_master_unique = non_master_df[~non_master_df['dato'].isin(master_dates)]

    concat_df = pd.concat([master_df, non_master_unique]).sort_values(by='dato')
    return concat_df.reset_index(drop=True)
