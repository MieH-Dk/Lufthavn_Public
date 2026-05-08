import streamlit as st
import pandas as pd
import io
from datetime import datetime
import calendar
from Selskaber.SGH import SGH_parser
from Selskaber.Lufthansa import Lufthansa_parser
from Selskaber.Aviator_DTO import DTO_parser
from Selskaber.Menzies import Menzies_parser



import io
st.header("Skemalægningsgenerator af Mie Harder!")
st.subheader("Følg instruktionerne nedenfor for at generere en fil til brug for skemalægning i lufthavnen")

month_of_choice = st.text_input("Hvilken måned vil du gerne have en skemafil for? Skriv måneden på dansk, fx 'april' eller 'maj'")
month_of_choice = month_of_choice.lower().capitalize()

"""SGH HERE"""
SGH_file = st.file_uploader("Herunder skal du uploade SGH-filen", type=["xlsx"])

"""LUFTHANSA HERE"""
Lufthansa_file = st.file_uploader("Herunder skal du uploade Lufthansa-filen", type=["xlsx"])


"""AVIATOR HERE"""
DTO_file = st.file_uploader("Herunder skal du uploade Aviator-filen", type=["xlsx"])

    
"""MENZIES HERE"""
Menzies_file = st.file_uploader("Herunder skal du uploade Menzies-filen", type=["xlsx"])


process = st.button("Generer fil")
if process:
    st.write("OK - Jeg går i gang!")
    if SGH_file:
        st.write("SGH data indlæses...")
        SGH_df = SGH_parser.format_SGH(SGH_file)
        st.write("SGH data indlæst med succes.")
    else:
        SGH_df = None
    if Lufthansa_file:
        st.write("Lufthansa data indlæses...")
        Lufthansa_df = Lufthansa_parser.lufthansa_final_df(Lufthansa_file)
        st.write("Lufthansa data indlæst med succes.")
    else:
        Lufthansa_df = None
    if DTO_file:
        st.write("Aviator data indlæses...")
        DTO_df = DTO_parser.format_DTO(DTO_file)
        st.write("Aviator data indlæst med succes.")
    else:    
        DTO_df = None
    if Menzies_file:
        st.write("Menzies data indlæses...")
        Menzies_df = Menzies_parser.menzies_final_df(Menzies_file)
        st.write("Menzies data indlæst med succes.")
    else:
        Menzies_df = None

    dfs = [df for df in [SGH_df, Lufthansa_df, DTO_df, Menzies_df] if df is not None]

    if dfs:
        all_flights = (
            pd.concat(dfs)
            .sort_values(by=["dato", "tid"])
            .reset_index(drop=True)
        )
    else:
        all_flights = pd.DataFrame()
    if all_flights.empty:
        st.write("No data available for the selected month.")
    else:
        
        import schedule_maker
        st.write("Genererer skemafil... Vent bare lidt længere nu!")
        all_flights['dato'] = pd.to_datetime(all_flights['dato'])
        all_clean = all_flights[(all_flights['måned']==month_of_choice)] #kigger både på  clean og wr
        year_string = str(all_clean['dato'].iloc[0].year) #only to name the excel file at the end
        all_clean = schedule_maker.create_df_with_search_guard(all_clean)
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
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for i in range(days_in_month):
                day = i + 1
                st.write(f'Now creating {day} / {days_in_month}')
                day_list = schedule_maker.one_day_schedule(day, all_clean)
                df = pd.DataFrame(
                    day_list[1:],
                    columns=day_list[0]
                )
                empty_sch = schedule_maker.create_empty_schedule()
                empty_sch.to_excel(
                    writer,
                    sheet_name=str(day),
                    index=False,
                    startcol=5
                )
                df.to_excel(
                    writer,
                    sheet_name=str(day),
                    index=False,
                    startrow=len(empty_sch) + 7
                )
                single_day = all_clean[
                    all_clean['dato'].dt.day == day
                ].copy()
                single_day['dato'] = single_day['dato'].dt.date
                single_day['tid'] = pd.to_datetime(
                    single_day['tid'],
                    format='%H:%M:%S'
                ).dt.time
                single_day.to_excel(
                    writer,
                    sheet_name=str(day),
                    index=False,
                    startrow=1,
                    startcol=83
                )
                worksheet = writer.sheets[str(day)]
                worksheet.set_column(0, 1, 5)
                worksheet.set_column(2, 4, 7)
                worksheet.set_column(5, 7, 10)
                worksheet.set_column(8, 79, 2.2)
                worksheet.set_column(80, 80, 18)
                worksheet.set_column(83, 85, 12)
        output.seek(0)

        st.download_button(
            label="Download Excel file",
            data=output,
            file_name=f'indmødetal_{month_of_choice}_{year_string}_created_{schedule_maker.current_date_str}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )