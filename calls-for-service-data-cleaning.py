import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import arange

calls = pd.read_csv('../input/Call_Data.csv')

#identify and remove rows with null values
print(calls.info(null_counts = True))
calls = calls.dropna()
print(calls.info(null_counts = True))

#convert column names to snake_case
calls.columns = (calls.columns
                .str.strip()
                .str.replace(" ", "_")
                .str.lower()
                )

#convert columns with dates into a uniform format
calls['arrived_time'] = pd.to_datetime(calls['arrived_time'], format = '%b %d %Y %H:%M:%S:%f%p')
calls['original_time_queued'] = pd.to_datetime(calls['original_time_queued'], format = '%m/%d/%Y %H:%M:%S %p')
calls['arrived_time'] = calls['arrived_time'].dt.strftime('%m/%d/%Y %H:%M:%S %p')
calls['arrived_time'] = pd.to_datetime(calls['arrived_time'], format = '%m/%d/%Y %H:%M:%S %p')

#create new columns with year, month and day
calls['year'] = pd.DatetimeIndex(calls['original_time_queued']).year
calls['month'] = pd.DatetimeIndex(calls['original_time_queued']).month
calls['day'] = pd.DatetimeIndex(calls['original_time_queued']).day

#remove rows that do not have a Beat identified
beats_list = ['B1', 'B2', 'B3', 'C1', 'C2', 'C3', 'D1', 'D2', 'D3', 'E1', 'E2', 'E3', 'F1', 'F2', 'F3', 'G1', 'G2', 'G3', 'J1', 'J2', 'J3', 'K1', 'K2', 'K3', 'L1',
'L2', 'L3', 'M1', 'M2', 'M3', 'N1', 'N2', 'N3', 'O1', 'O2', 'O3', 'Q1', 'Q2', 'Q3', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3', 'U1', 'U2', 'U3', 'W1', 'W2', 'W3']
calls = calls[calls['beat'].isin(beats_list)]

#remove unnecessary columns
calls = calls.drop(['priority', 'initial_call_type', 'original_time_queued', 'arrived_time'], axis = 1)

#remove rows with 'UNKNOWN' values in the Precinct column
calls = calls[calls['precinct'] != 'UNKNOWN']

#isolate calls that occurred in 2016 & 2017
calls_2016 = calls[calls['year'] == 2016]
calls_2017 = calls[(calls['year'] == 2017) & (calls['month'] <= 10)]
calls = pd.concat([calls_2016, calls_2017])

#remove extraneous characters in 'final_call_type' column
calls['final_call_type'] = calls['final_call_type'].str.replace("--", "")
calls['precinct'] = calls['precinct'].str.strip()

#isolate calls related to residential burglary
burglary_list = []
for b in calls['final_call_type'].unique():
    if 'BURG' in b and 'COMM' not in b:
        burglary_list.append(b)
burglary = calls[calls['final_call_type'].isin(burglary_list)]

#saving counts of burglary to call_type_counts dictionary
call_type_counts = {}
call_type_counts['burglary'] = burglary['final_call_type'].count()

#isolate calls related to car prowls
prowls_list = []
for t in calls['final_call_type'].unique():
    if 'CAR PROWL' in t:
        prowls_list.append(t)
prowls = calls[calls['final_call_type'].isin(prowls_list)]
call_type_counts['prowls'] = prowls['final_call_type'].count()

#isolate calls related to property damage
damage_list = []
for d in calls['final_call_type'].unique():
    if 'PROPERTY' in d and 'DAM' in d:
        damage_list.append(d)
damage = calls[calls['final_call_type'].isin(damage_list)]
call_type_counts['damage'] = damage['final_call_type'].count()

#isolate calls related to littering/dumping
litter_list = []
for l in calls['final_call_type'].unique():
    if 'LITT' in l or 'DUMP' in l:
        litter_list.append(l)
litter = calls[calls['final_call_type'].isin(litter_list)]
call_type_counts['litter'] = litter['final_call_type'].count()

#isolate calls related to automobile theft
theft_list = []
for t in calls['final_call_type'].unique():
    if 'THEF' in t and 'AUTO' in t:
        theft_list.append(t)
auto_theft = calls[calls['final_call_type'].isin(theft_list)]
call_type_counts['auto_theft'] = auto_theft['final_call_type'].count()

#isolate calls related to unsafe driving
traffic_list = []
for t in calls['final_call_type'].unique():
    if 'TRAFFIC -' in t and 'PAR' not in t:
        traffic_list.append(t)
traffic = calls[calls['final_call_type'].isin(traffic_list)]
call_type_counts['traffic'] = traffic['final_call_type'].count()

#isolate calls related to parking
parking_list = []
for p in calls['final_call_type'].unique():
    if 'PARKING' in p:
        parking_list.append(p)
parking = calls[calls['final_call_type'].isin(parking_list)]
call_type_counts['parking'] = parking['final_call_type'].count()

#create a function that provides counts for each concern by precinct
def group_by_prec(precinct):
    concern = ['burglary', 'prowls', 'damage', 'litter', 'auto_theft', 'traffic', 'parking']
    dataset = [burglary, prowls, damage, litter, auto_theft, traffic, parking]
    d = {}
    n = 0
    for c in concern:
        if c == 'burglary':
            group = dataset[n].groupby('precinct')['final_call_type'].count()
            d = {c:group[precinct]}
        else:
            group = dataset[n].groupby('precinct')['final_call_type'].count()
            d[concern[n]] = group[precinct]
        n = n + 1
    return d
    
n_concerns = group_by_prec('NORTH')
n_calls = calls[calls['precinct'] == 'NORTH'].shape
n_burglary_perc = n_concerns['burglary'] / n_calls[0]
s_concerns = group_by_prec('SOUTH')
w_concerns = group_by_prec('WEST')
sw_concerns = group_by_prec('SOUTHWEST')