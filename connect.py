import pandas as pd
import os
import math

#region functions
def sigmoid(i, count, spread, dx, dy, mode):
    xi = (i-1.0)*(12.0/(count-1.0))-6.0
    a = 1.0/(1.0+math.exp(-xi))
    x = a * dx
    y = (i-1.0)*(spread/(count-1.0))-(spread/2.0)
    if mode == 1:   
        y = ((spread/2.0)-y)-(spread/2.0)  
    y = dy + y
    return x, y

#x, y = sigmoid(i, resolution, spread / 2, abs(row['t_totalvotes'] - lastvotes), row['year'] - spread / 4, morevotes)

padleft = 13
padright = 2389
df = pd.read_csv(os.path.dirname(__file__) + '/state_test5.csv', engine='python') # test with , nrows=20
df2016 = df.loc[df['y'] == 2016]
df2016['x2t'] =(df2016['x2']-padleft)/(padright-padleft)
df2016['x3t'] =(df2016['x3']-min(df2016['x3']))/(max(df2016['x3'])-min(df2016['x3']))

df2016_x2t = df2016.groupby('state').agg({'x2t':'mean'}).reset_index()
df2016_x3t = df2016.groupby('state').agg({'x3t':'mean'}).reset_index()
dfjoin = pd.merge(df2016_x2t, df2016_x3t, on=['state'], how='left')

# df2016_x2t['x'] = df2016_x2t['x2t']
# df2016_x2t['y'] = 0
# df2016_x3t['x'] = df2016_x3t['x3t']
# df2016_x3t['y'] = 1
# dfunion = pd.concat([df2016_x2t, df2016_x3t])
# print(dfjoin)

data = []
df_group = dfjoin.groupby(['state'])
resolution = 31
for name, group in df_group: 
    for i in range (1, resolution + 1):
        x, y = sigmoid(i, resolution, 1, group['x2t'].values[0] - group['x3t'].values[0], 0, True)
        data.append([name, group['x3t'].values[0] + x, y])

df_sig = pd.DataFrame(data, columns=['state', 'x', 'y'])
print(df_sig)
df_sig.to_csv(os.path.dirname(__file__) + '/connect.csv', encoding='utf-8', index=False)