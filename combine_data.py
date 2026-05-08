import pandas as pd

from Selskaber.Norwegian import Norwegian_parser
from Selskaber.Lufthansa import Lufthansa_parser
from Selskaber.Aviator_DTO import DTO_parser
from Selskaber.SGH import SGH_parser
from Selskaber.Småselskaber import parser_leftover
from Selskaber.Menzies import Menzies_parser

print('SGH loading... \n')
SGH_df = SGH_parser.format_SGH('Selskaber/SGH/Trafik SGH_202604.xlsx')
#print('Norwegian loading...\n')
#Norwegian_df= Norwegian_parser.norwegian_final_df( 'Selskaber/Norwegian/Norwegian_202510.xlsx', 'Selskaber/Norwegian/Norwegian_202510.xlsx')
print('\n Lufthansa loading...\n')
Lufthansa_df = Lufthansa_parser.lufthansa_final_df('Selskaber/Lufthansa/Lufthansa_202604.xlsx')
print('DTO loading...\n')
Aviator_df= DTO_parser.format_DTO('Selskaber/Aviator_DTO/datafiler/Aviator_202604MAJ.xlsx')
#print('American Airlines loading...\n')
#AA_df = parser_leftover.format_AA("Selskaber/Småselskaber/AA American Airlines.xlsx")
#print('Delta loading...\n')
#Delta_df = parser_leftover.format_delta("Selskaber/Småselskaber/Delta01022024.xlsx")
#print('Middle Eastern loading...\n')
#ME_df = parser_leftover.format_ME("Selskaber/Småselskaber/ME_16092024.xlsx")
#print('Turkish Airlines loading...\n')
#TK_df = parser_leftover.format_TK("Selskaber/Småselskaber/TK_16092024.xlsx")
print('Menzies loading...\n')
Menzies_df = Menzies_parser.menzies_final_df("Selskaber/Menzies/Datafiler/Menzies_202604.xlsx")
def TOTAL_DATA():
    return pd.concat([SGH_df, Lufthansa_df, Aviator_df, Menzies_df]).sort_values(by=['dato', 'tid']).reset_index(drop=True)
    #return pd.concat([SGH_df, Norwegian_df, Lufthansa_df, Aviator_df, Menzies_df]).sort_values(by=['dato', 'tid']).reset_index(drop=True)
    #return pd.concat([SGH_df, Norwegian_df, Lufthansa_df, AA_df, Delta_df, ME_df, TK_df, Aviator_df, Menzies_df]).sort_values(by=['dato', 'tid']).reset_index(drop=True)
print('Done! Now for data processing! \n')