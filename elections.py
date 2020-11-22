import pandas as pd
import os
import math

df = pd.read_csv(os.path.dirname(__file__) + '/state_test.csv', engine='python') # test with , nrows=20
data = []
df_group = df.groupby(['state', 'legacy'])
#sortflag = True
path = 0
for name, group in df_group: 
    upgroup = group.loc[group['segment'] == 1].sort_values('y', ascending=True)
    for index, row in upgroup.iterrows():
        row['path'] = path
        data.append(row)
        path += 1
    downgroup = group.loc[group['segment'] == 2].sort_values('y', ascending=False)
    for index, row in downgroup.iterrows():
        row['path'] = path
        data.append(row)
        path += 1
    path = 0

df_state = pd.DataFrame(data, columns=['x', 'y', 'state', 'party', 'path', 'legacy', 'term', 'segment'])
print(df_state)
df_state.to_csv(os.path.dirname(__file__) + '/state_test2.csv', encoding='utf-8', index=False)