import numpy as np
import pandas as pd
from datetime import datetime, timedelta

airlines_to_keep = ['AF', 'EY', 'IA', 'KL', 'LG', 'VN','LO', 'OU', 'RC', 'SN', 'UD', 'CA', 'FI', 'FH', 'MU', 'AZ', 'NO', 'WS'] #EY og MU er WB men kun arrival
wb_airlines = ['EY', 'CA', 'MU', 'VN']
month_mapping = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober',11: 'November',12: 'December'}
weekday_mapping = {
    'Monday': 'Mandag',
    'Tuesday': 'Tirsdag',
    'Wednesday': 'Onsdag',
    'Thursday': 'Torsdag',
    'Friday': 'Fredag',
    'Saturday': 'Lørdag',
    'Sunday': 'Søndag'
}
def format_hour(datetime):
    """Hjælpefunktion til at formattere tid med halvtimesintervaller"""
    hour=datetime.strftime('%H')
    minute=datetime.minute
    if minute<30:
        return f"{hour}:00-{hour}:29"
    else:
        return f"{hour}:30-{hour}:59"
    
def format_DTO(file_name):
    dto_data=pd.read_excel(file_name)
    dto_data=dto_data[dto_data['Carrier'].isin(airlines_to_keep)].reset_index(drop=True)
    dto_data = dto_data[dto_data['In/out']=='Arrival'] #skal kun bruge arrivals
    dto_data['uge']=dto_data['Date of operation'].dt.isocalendar().week
    dto_data['Flight']=dto_data['Carrier']+' '+dto_data['Flight'].astype(str)
    dto_data['tids_slot']=dto_data['Time'].apply(format_hour)
    dto_data['Ugedag']=dto_data['Weekday'].map(weekday_mapping)
    dto_data['måned']=dto_data['Date of operation'].dt.month
    dto_data['måned']=dto_data['måned'].map(month_mapping)
    dto_data=dto_data[['Flight', 'From','Date of operation', 'uge', 'Ugedag', 'måned', 'Time', 'tids_slot', 'Carrier', 'Aircraft']]
    dto_data=dto_data.rename(columns={'Date of operation':'dato', 'From': 'Dest', 'Time': 'tid'})
    dto_data['Rengøringstype'] = 'clean'
    dto_data['WB']= (dto_data['Carrier'].isin(wb_airlines))
    dto_data['WB'] = dto_data['WB'].map({True: 'A', False: 'False'})
    dto_data['dato'] = dto_data['dato'].dt.date
    dto_data['Origin_file'] = 'Aviator'
    dto_data = dto_data.rename(columns={'Carrier': 'AL', 'Aircraft': 'Flytype'})
    return dto_data[['Flight', 'Dest', 'dato', 'uge', 'Ugedag', 'måned', 'tid', 'tids_slot','Rengøringstype', 'Origin_file', 'WB', 'Flytype', 'AL']].sort_values(by = 'dato').reset_index(drop=True)
