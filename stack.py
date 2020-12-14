# Written by: Nick Gerend, @dataoutsider
# Viz: "Party Lines", enjoy!

import pandas as pd
import os
import math

df = pd.read_csv(os.path.dirname(__file__) + '/1976-2016-president.csv', engine='python') # test with , nrows=20
df['term'] = df['year']

df2016 = df.loc[df['year'] == 2016]
df2016 = df2016.groupby('state').agg({'totalvotes':'max'}).reset_index()
df2016['2016_votes'] = df2016['totalvotes']
df2016['2016_rank'] = df2016['totalvotes'].rank(ascending=False)
df2016['t_totalvotes'] = df2016['totalvotes']/100000

df2 = pd.read_csv(os.path.dirname(__file__) + '/state_test3.csv', engine='python') # test with , nrows=20
#df3 = pd.merge(df2, df, on=['state', 'term'], how='inner')
df3 = pd.merge(df2, df2016, on=['state'], how='left')
#df3.to_csv(os.path.dirname(__file__) + '/state_test_1.csv', encoding='utf-8', index=False)
#print(df3)
df3['x2'] = 0
data = []
df_group = df3.groupby(['term'])
separation = 20.0
xadd = 0.0
istate = 1.0
ix = 0
for name, group in df_group: 
    year = group.sort_values('2016_rank', ascending=True)
    for index, row in year.iterrows():       
        if row['2016_rank'] != istate:
            xadd += ix
        row['x2'] = row['x'] + xadd + separation * row['2016_rank']
        data.append(row)
        istate = row['2016_rank']
        ix = row['t_totalvotes']
    istate = 1
    ix = 0
    xadd = 0

df_state = pd.DataFrame(data, columns=df3.columns)
print(df_state)
df_state.to_csv(os.path.dirname(__file__) + '/state_test4.csv', encoding='utf-8', index=False)