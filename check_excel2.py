import pandas as pd

print('Reading dustbins.xlsx:')
df = pd.read_excel('services/guide_service/data/dustbins.xlsx')
print('Columns:', list(df.columns))
print('First row name:', repr(df.iloc[0, 2]))

print('\nReading dustbins_with_types.xlsx:')
df2 = pd.read_excel('services/guide_service/data/dustbins_with_types.xlsx')
print('Columns:', list(df2.columns))
print('First row name:', repr(df2.iloc[0, 2]))

print('\nReading original station info:')
df3 = pd.read_excel('\u5783\u573e\u7ad9\u70b9\u4fe1\u606f\u8868.xlsx')
print('Columns:', list(df3.columns))
print('First row name:', repr(df3.iloc[0, 2]))
