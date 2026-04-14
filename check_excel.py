import pandas as pd
dustbins_df = pd.read_excel('services/guide_service/data/dustbins_with_types.xlsx')
print('Columns:', dustbins_df.columns.tolist())
print('First station name:', repr(dustbins_df.iloc[0]['站点名称']))
