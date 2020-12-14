# Written by: Nick Gerend, @dataoutsider
# Viz: "Party Lines", enjoy!

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

def state_shape(data, spread, resolution, mirror):
    #region inputs
    istate = 0
    idata = 0
    legacy = 0 #party group
    lastparty = ''  
    lastflip = False
    lastvotes = 0
    lastterm = 0
    morevotes = 1
    lastrow = None
    start = 0
    end = 0
    it = 0
    xi = 0
    a = 0
    x = 0
    y = 0
    flip = 0
    flipset = 0
    intial_x = 0
    segment = 1
    if mirror: 
        flip = 1
        flipset = 1
        segment = 2
    #endregion
    
    #region state loop 
    for name, group in df.groupby(['state']):
        for index, row in group.iterrows():            
            if istate == 0:
                if mirror:
                    intial_x = row['t_totalvotes']
                data.append([intial_x, row['year'], row['state'], row['party'], -1, legacy, row['year'], segment])              
            else: 
                if row['t_totalvotes'] > lastvotes:
                    morevotes = 0           
                if row['party'] == lastparty: 
                    #region set x value
                    if flip == 0:
                        x = 0
                    else:
                        x = row['t_totalvotes']  
                    #endregion           
                    data.append([x, row['year'], row['state'], row['party'], -1, legacy, row['year'], segment])
                    data.append([x, row['year'], row['state'], row['party'], -1, legacy, lastrow['year'], segment])
                    #region sigmoid fill
                    if lastflip and flip == 1: # from baseline, btm of current nide (1 of 3)                 
                        for i in range (1, resolution + 1):
                            x, y = sigmoid(i, resolution, spread / 2, abs(row['t_totalvotes'] - lastvotes), row['year'] - spread / 4, morevotes)
                            data.append([min(lastvotes,row['t_totalvotes']) + x, y, row['state'], lastparty, -1, legacy, lastterm, segment])

                    elif flip == 1: # solve for btm of current node, top of last node (2 of 3)
                        for i in range (1, resolution + 1):
                            x, y = sigmoid(i, resolution, spread, abs(row['t_totalvotes'] - lastvotes), row['year'] - spread / 2, morevotes)
                            data.append([min(lastvotes,row['t_totalvotes']) + x, y, row['state'], lastparty, -1, legacy, lastterm, segment])
                    #endregion
                    lastflip = False
                else: #flip
                    #region party flip (x end to end)
                    if flip == 0:
                        start = 1
                        end = resolution + 1
                        it = 1
                    else:
                        start = resolution + 1
                        end = 1
                        it = -1
                    for i in range (start, end, it):
                        x, y = sigmoid(i, resolution, spread, row['t_totalvotes'], row['year'], flip)
                        data.append([x, y, row['state'], lastparty, -1, legacy, lastterm, segment])
                        if i == (resolution -1) / 2.0 + 1: #add beginning point to new legacy
                            legacy += 1
                            lastparty = row['party']
                            lastterm = row['year']
                            data.append([x, y, row['state'], row['party'], -1, legacy, row['year'], segment])
                    #endregion              
                    if flip == 0:
                        flip = 1
                        lastflip = True
                    else: # back to baseline, solve top of last node (3 of 3)                    
                        #region sigmoid fill
                        for i in range (1, resolution + 1):
                            x, y = sigmoid(i, resolution, spread / 2, abs(row['t_totalvotes'] - lastvotes), row['year'] - (spread - spread / 4), morevotes)
                            data.append([min(lastvotes,row['t_totalvotes']) + x, y, row['state'], lastrow['party'], -1, legacy - 1, lastrow['year'], segment])   
                        #endregion                   
                        flip = 0
                        lastflip = True
            #region reset counters and pointers
            istate += 1
            idata += 1
            lastparty = row['party']
            lastvotes = row['t_totalvotes']
            lastterm = row['year']
            morevotes = 1
            lastrow = row
            #endregion
        #region reset counters
        istate = 0
        legacy = 0
        flip = flipset
        #endregion
    #endregion
#endregion

#region data
df = pd.read_csv(os.path.dirname(__file__) + '/1976-2016-president.csv', engine='python') # test with , nrows=20
df_group = df.groupby(['year', 'state']).agg({'candidatevotes':'max'}).dropna().reset_index()
df = pd.merge(df, df_group, on=['year', 'state'], how='inner')
df = df.loc[df['candidatevotes_x'] == df['candidatevotes_y']]
df['state_rank'] = df.groupby('year')['totalvotes'].rank(ascending=False)
df['t_totalvotes'] = df['totalvotes']/100000
df = df.sort_values(['year', 'state_rank'], ascending=[True, True]).reset_index()
#endregion

data = []
spread = 2 #4years
resolution = 31 # non-even number

state_shape(data, spread, resolution, False)
state_shape(data, spread, resolution, True)

df_state = pd.DataFrame(data, columns=['x', 'y', 'state', 'party', 'path', 'legacy', 'term', 'segment'])
print(df_state)
df_state.to_csv(os.path.dirname(__file__) + '/state_test.csv', encoding='utf-8', index=False)