if __name__ == "__main__":
    month_of_choice = 'Maj' #Måned skal stå på dansk


import numpy as np
import pandas as pd
import math
import sys
from datetime import datetime, timedelta
if __name__ == "__main__":
    import combine_data
    all_flights = combine_data.TOTAL_DATA()

current_date_str = str(datetime.today().strftime('%Y-%m-%d'))

SK_search_guard_destinations = ['EWR','BOS', 'SFO', 'LAX', 'JFK', 'ORD', 'ATL', 'IAD', 'MIA'] #should only be search and guard for these destinations
def create_df_with_search_guard(df):
    """Removes irrelevant WB departures and labels remaining WB departures is dublicated. One is labeled Search and the other one Guard.
    This function should be the first to be used."""
    departure_mask = df['WB'] == 'D' #only departures
    false_destination_mask = ~df['Dest'].isin(SK_search_guard_destinations) #all destinations not in list
    al_mask = df['AL'] == 'SK' #SAS
    total_match = departure_mask & false_destination_mask & al_mask #all sk departures with destinations not in list
    rest_irr_match = departure_mask & ~al_mask #all non SK departures (WB)
    df = df[~total_match & ~rest_irr_match].reset_index(drop=True)
    true_destination_mask = df['Dest'].isin(SK_search_guard_destinations)
    departure_mask = df['WB'] == 'D'
    al_mask = df['AL'] == 'SK'
    true_mask = departure_mask & true_destination_mask & al_mask #these are the ones, we want to duplicate
    true_rows = df[true_mask] #only the rows which fulfills the criterias
    df = df[~true_mask] #the rest of the df
    duplicated_rows = true_rows.copy()
    duplicated_rows.loc[:, 'WB'] = 'Guard'
    true_rows.loc[:, 'WB'] = 'Search'
    result_df = pd.concat([df, duplicated_rows, true_rows], ignore_index=True)
    result_df['Flytype'] = result_df['Flytype'].astype(str)
    return result_df.sort_values(by=['dato', 'tid']).reset_index(drop=True)

if __name__ == "__main__":
    all_flights['dato'] = pd.to_datetime(all_flights['dato'])
    #all_clean = all_flights[(all_flights['måned']==month_of_choice) & (all_flights['Rengøringstype']== 'clean') ] #kigger ikke på wr
    all_clean = all_flights[(all_flights['måned']==month_of_choice)] #kigger både på  clean og wr
    year_string = str(all_clean['dato'].iloc[0].year) #only to name the excel file at the end
    all_clean = create_df_with_search_guard(all_clean)
    days_in_month = max(list(all_clean['dato'])).day #antallet af dage i den angivne måned

rules=pd.read_excel('Indmødetal/Regler til Mie.xlsx', sheet_name='clean') #indlæser datafilen med regler
rules['Selskab'] = rules['Selskab'].astype(str)
columns_list=['Antal', 'Tid', 'Flight', 'Flytype', 'Dest', 'STA', 'STA +', 'STD -',#denne liste er kolonnerne til den endelige fil
                '6',' ',' ',' ',
                '7',' ',' ',' ',
                '8',' ',' ',' ',
                '9',' ',' ',' ',
                '10',' ',' ',' ',
                '11',' ',' ',' ',
                '12',' ',' ',' ',
                '13',' ',' ',' ',
                '14',' ',' ',' ',
                '15',' ',' ',' ',
                '16',' ',' ',' ',
                '17',' ',' ',' ',
                '18',' ',' ',' ',
                '19',' ',' ',' ',
                '20',' ',' ',' ',
                '21',' ',' ',' ',
                '22',' ',' ',' ',
                '23',' ',' ',' ', 'Kommentar'
                ]

#functions 
def match_rules(flight):
    """This function matches a flight with the corresponsing rule from the rule-file.
    Input: A row of the flights df. i.e. information about a single flight
    Returns: A row of the rules df, which corresponds to the flight in question."""
    wr_match = pd.DataFrame([{
    'Flytype': np.nan,
    'Selskab': np.nan,
    'STA +': '00:10:00',  
    'STD -': np.nan,  
    'Tid': '00:07:00', 
    'Antal': 1, 
    'Opgave': 'Waste Removal',
    'Kommentar': 'Waste Removal',
    }], columns =  ['Flytype', 'Selskab', 'STA +', 'STD -', 'Tid', 'Antal', 'Opgave', 'Kommentar'])
    if flight['Rengøringstype'] == 'wr':
        return wr_match
    match = rules.loc[rules['Selskab']==flight['AL']]
    match_copy = match.copy()
    match_copy['Flytype'] = match_copy['Flytype'].astype(str)
    further_match = match_copy.loc[match_copy['Flytype'] == str(flight['Flytype'])]
    if further_match.empty:
        return match[match['Flytype'].isna()]
    else: #if there is one or more further matches then we need to check if search/guard
        if flight['WB'] not in ['Search', 'Guard']:
            return further_match
        else:
            wb_match = further_match.loc[further_match['Opgave'] == flight['WB']]
            return wb_match 
def ceil_dt(dt):
    """Function for rounding a time up to nearest fifteen minutes.
    input: timestamp.
    Returns: the time but rounded up to the nearest 15 minutes"""
    t_delta = timedelta(minutes=15)
    time = dt + (datetime.min - dt) % t_delta
    return time
def number_of_staff(flight):
    """ Function for determining the number of staff needed to clean the aircraft
    input: A row of the flights df. i.e. information about a single flight
    Returns: the number of staff needed to clean the aircraft"""
    match = match_rules(flight)
    if match.empty:
        match = rules.loc[rules['Kommentar']== 'No Match']
    return match['Antal'].iloc[0]        
def time_spend_cleaning(flight):
    """ Function for determining the time needed to clean the aircraft
    input: A row of the flights df. i.e. information about a single flight
    Returns: the amount of time needed to clean the aircraft"""
    match = match_rules(flight)
    if match.empty:
        match = rules.loc[rules['Kommentar']== 'No Match']
        print('The following flight has no match: \n', flight)
    return match['Tid'].iloc[0]
def later_arrival(flight):
    """ Function for determining whether or not staff should arrive later to the aircraft
    input: A row of the flights df. i.e. information about a single flight
    Returns either NaN or the time of delayed arrival for the staff on site. e.g. if staff is supposed to meet at the plane later"""
    match = match_rules(flight)
    if not match.empty:
        return match['STA +'].iloc[0]
    else:
        return None  
def early_arrival(flight):
    """ Function for determining whether or not staff should arrive earlier to the aircraft
    input: A row of the flights df. i.e. information about a single flight
    Returns: either NaN or the time of early arrival for the staff on site. e.g. if staff is supposed to meet at the plane later"""
    match = match_rules(flight)
    if not match.empty:
        return match['STD -'].iloc[0]
    else:
        return None
def comment(flight):
    """A function for determining what to write in the comment field in the excel file. This should be either search, guard or nothing.
    input: A row of the flights df. i.e. information about a single flight
    Returns: Either Search, Guard or None
    """
    #if flight['WB'] in ['Search', 'Guard']:
    #    return flight['WB']
    #else:
    #    return None
    match = match_rules(flight)
    if not match.empty:
        if flight['WB'] in ['Search', 'Guard']:
            return flight['WB']
        else:
            return match['Kommentar'].iloc[0]
    else:
        return None
def start_time(flight):
    """A function for determining what time staff should be by the aircraft.
    input: A row of the flights df. i.e. information about a single flight
    Returns: A datetime object describing start time
    """
    time = flight['tid']
    time = pd.to_datetime(time)
    starttime = ceil_dt(time)
    if (isinstance(flight['STA +'], float)) & (isinstance(flight['STD -'], float)): #nan is a float
        return starttime.time()
    elif (flight['STA +'] is None) & (flight['STD -'] is None):
        return starttime.time()
    else:
        if isinstance(flight['STD -'], float): #if STA + is not a nan
            extra_time = pd.to_datetime(str(flight['STA +']))
            return ((starttime-datetime.strptime('00:00:00', '%H:%M:%S')+extra_time).time())
        else: #this means that it is a departure flight, so either search or guard
            prior_time = pd.to_datetime(str(flight['STD -']))
            starttime = pd.to_datetime(starttime)
            return pd.to_datetime(starttime - timedelta(hours=prior_time.hour, minutes=prior_time.minute, seconds=prior_time.second)).time()
def create_empty_schedule():
    """A function for creating an empty schedule, which should remain empty and is placed at the top of the excel file
    input: 
    Returns: A dataframe, which is the empty schedule
    """
    empty_schedule=['Brutto', 'Antal', 'Vagt', #denne liste er kolonnerne til detoppe skema øverst i filen
              '6',' ',' ',' ',
              '7',' ',' ',' ',
              '8',' ',' ',' ',
              '9',' ',' ',' ',
              '10',' ',' ',' ',
              '11',' ',' ',' ',
              '12',' ',' ',' ',
              '13',' ',' ',' ',
              '14',' ',' ',' ',
              '15',' ',' ',' ',
              '16',' ',' ',' ',
              '17',' ',' ',' ',
              '18',' ',' ',' ',
              '19',' ',' ',' ',
              '20',' ',' ',' ',
              '21',' ',' ',' ',
              '22',' ',' ',' ',
              '23',' ',' ',' ', 'Kommentar'
              ]
    list_of_shifts = ['05:45-12:45','06:45-14:15','06:45-13:00','06:45-15:15','07:00-15:00','07:00-13:00','10:00-18:00','10:00-20:00','10:00-15:00','11:30-21:00',
                        '14:00-18:00','13:15-21:00','13:15-21:15','13:15-22:45','14:00-22:45','14:30-22:45','14:45-22:45','15:00-22:45','16:00-22:45','17:00-22:45','15:30-20:30','15:00-20:00']
    list_of_lists_schedule = [empty_schedule]
    for shift in list_of_shifts:
        list_to_append = [' '] * len(empty_schedule)
        list_to_append[2] = shift
        list_of_lists_schedule.append(list_to_append)
    return pd.DataFrame(list_of_lists_schedule[1:], columns=list_of_lists_schedule[0])
def create_schedule_line(flight):
    """A function for creating a line to be added to the final schedule consisting of data from a single flight
    input: A row of the flights df. i.e. information about a single flight
    Returns: A list of information about the flight to be added to the schedule
    """
    list_to_return=[' ']*81
    list_to_return[0]= flight['Antal']
    list_to_return[1]= flight['Rengøringstid']
    list_to_return[2]= flight['Flight']
    list_to_return[3]= flight['Flytype']
    list_to_return[4]= flight['Dest']
    list_to_return[5]= flight['tid']
    list_to_return[6]= flight['STA +']
    list_to_return[7]= flight['STD -']
    list_to_return[-1]= flight['Kommentar']
    start_hour = flight['Start tid'].hour
    start_quarters = flight['Start tid'].minute //15
    first_index = 8+((start_hour-6)*4)+start_quarters
    for i in range(flight['Rengøringstid_kvarter']):
        list_to_return[first_index] = flight['Antal']
        first_index+=1
    return list_to_return
def one_day_schedule(day_number, df):
    """ Function for creating all information about all flights for a single day
    Input: an integer describing the day number
           dataframe consisting all flights
    Returns: a list of lists containing the schedule for a single day"""
    list_to_return = [columns_list] #should contain lists for each flight
    day_df = df[df['dato'].dt.day == day_number].copy()  # Create a copy to avoid SettingWithCopyWarning
    day_df['Antal']=day_df.apply(number_of_staff, axis=1)
    day_df['Rengøringstid']=day_df.apply(time_spend_cleaning, axis=1)
    day_df['Rengøringstid'] = pd.to_datetime(day_df['Rengøringstid'], format='%H:%M:%S').dt.time
    day_df['tid'] = day_df['tid'].astype(str)  # Convert 'tid' column to string
    full_day_df = day_df.copy()
    night_df = day_df[(day_df['tid'] < '05:45:01') | (day_df['tid'] > '22:29:59')]  # Filter based on time string
    day_df = day_df[(day_df['tid'] > '05:45:00') & (day_df['tid'] < '22:30:00')]
    #day_df['Rengøringstid'] = pd.to_timedelta(day_df['Rengøringstid'])
    day_df['Rengøringstid_kvarter'] = day_df['Rengøringstid'].apply(lambda x: math.ceil((x.hour * 60 + x.minute) / 15))
    day_df['STA +']= day_df.apply(later_arrival, axis=1)
    day_df['STD -'] = day_df.apply(early_arrival, axis=1)
    day_df['Start tid'] = day_df.apply(start_time, axis=1)
    day_df['Kommentar'] = day_df.apply(comment, axis=1)
    day_df = day_df.sort_values(by= 'Start tid').reset_index(drop=True)
    for index, row in day_df.iterrows():
        list_to_return.append(create_schedule_line(row))
    return list_to_return

if __name__ == "__main__":
    print('\n Wait while the ExCel file is created...')

    #below creates the schedule excel file
    with pd.ExcelWriter(f'Indmødetal/indmødetal_{month_of_choice}_{year_string}_created_{current_date_str}.xlsx', engine='xlsxwriter') as writer:
        for i in range(days_in_month):
                day = i+1
                print('Now creating', i+1, '/', days_in_month)
                day_list = one_day_schedule(day, all_clean)
                df=pd.DataFrame(day_list[1:], columns=day_list[0])#.sort_values(by = 'STA')
                empty_sch = create_empty_schedule()
                empty_sch.to_excel(writer, sheet_name = str(day), index = False, startcol = 5)
                df.to_excel(writer, sheet_name = str(day), index = False, startrow = len(empty_sch)+7)
                single_day = all_clean[all_clean['dato'].dt.day == day].copy()
                single_day['dato'] = single_day['dato'].dt.date
                single_day['tid'] = pd.to_datetime(single_day['tid'], format='%H:%M:%S').dt.time
                single_day = single_day#.sort_values(by = 'tid')
                single_day.to_excel(writer, sheet_name= str(day), index = False, startrow = 1, startcol = 83)
                worksheet = writer.sheets[str(day)]
                #worksheet.write('AJ60', '=SUM(AJ2:AJ59)')
                worksheet.set_column(0, 1, 5)
                worksheet.set_column(2, 4, 7)
                worksheet.set_column(5, 7, 10)
                worksheet.set_column(8, 79, 2.2)
                worksheet.set_column(80, 80, 18)
                worksheet.set_column(83, 85, 12)

    print('The schedule has been created succesfully! \n')