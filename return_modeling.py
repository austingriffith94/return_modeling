# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 13:14:57 2017

@author: Austin
"""

import sys
import csv
import pandas as pd
import datetime
import numpy as np
import pandas_datareader as pdr
import re

csv1 = 'tickers_nasd.csv'
csv2 = 'tickers_nyse.csv'
min_cap = 500*(10**6)
source = 'yahoo'
start_date = '2000-01-01'
end_date = '2017-11-17'

# reads csv, gets ticker values
class reader:
    def __init__(self,name,min):
        self.name = name
        self.min = min
        self.data = pd.DataFrame.empty
        
    def csvr(self):
        data = pd.read_csv(self.name)
        data = data.drop_duplicates(['Symbol'])
        data['Symbol'] = data['Symbol'].str.strip()
        data = data[data.MarketCap.str.contains('nan') == False]
        data['Dol'] = data.MarketCap.str[-1:]
        data['Val'] = data.MarketCap.str[1:-1]
        data['Val'] = pd.to_numeric(data['Val'])
        data['Cap'] = (data['Val']*(10**9)).where(data['Dol'] == 'B')
        data['mil'] = (data['Val']*(10**6)).where(data['Dol'] == 'M')
        data['Cap'] = data['Cap'].fillna(data['mil'])
        data = data[data['Cap'] >= self.min]  
        self.data = data
        return(data)
        
    def tickers(self):
        t = self.data['Symbol']
        return(t)
        
# combines ticker data frames     
def combine_tickers(t1,t2):
    all_t = [t1,t2]
    ticker = pd.concat(all_t).reset_index(drop=True)
    return(ticker)
        
# pulls api data and saves it as hdf5
# reads hdf5 api data file
class api:
    def __init__(self,tickers,source,start,end):
        self.tickers = tickers
        self.source = source
        self.start = start
        self.end = end
    
    def api_save(self):
        api_data = pdr.DataReader(self.tickers,self.source,self.start,self.end)
        api_data.to_hdf('api_data.h5','api_data',format = 't')

    def api_read(self):
        file = pd.read_hdf('api_data.h5')
        return(file)
        
        
class xy:    
    def __init__(self,date):
        self.date = date
    
    def log_ret(self,x,adj):
        b = -1*x
        loc = adj.index.get_loc(self.date)
        adj_date = adj.iloc[loc]
        
        if x > adj.shape[0]:
            window = adj[adj.index < self.date].iloc[0]
        else:
            window = adj[adj.index < self.date].iloc[b]
            
        loc1 = adj.index.get_loc(window.name)
        adj_1 = adj.iloc[loc1]
        adj_log = np.log(adj_date/adj_1)
        return(adj_log)
        
    def move_avg(self,x):
        pass


# read tickers from csv
# pull price date from yahoo api
nasd = reader(csv1,min_cap)
nyse = reader(csv2,min_cap)
data = nasd.csvr()
nyse.csvr()
ticker1 = nasd.tickers()
ticker2 = nyse.tickers()
ticker = combine_tickers(ticker1,ticker2)
yahoo = api(ticker,source,start_date,end_date)
# yahoo.api_save() # gets the api data from yahoo finance
file = yahoo.api_read()

# get log returns of adj close
# moving average
date = '2000-05-16'
adj = file.loc['Adj Close']

n = [1,5,22]
stats = xy(date)

log1 = stats.log_ret(1,adj)
log5 = stats.log_ret(5,adj)
log22 = stats.log_ret(22,adj)
log = pd.concat([log1,log5,log22], axis=1)

    