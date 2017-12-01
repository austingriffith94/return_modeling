# Austin Griffith
# 11/30/2017
# Return Modeling
# Python 3.6.3

# library import
import statsmodels.api as sm
import pandas as pd
import numpy as np
import pandas_datareader as pdr

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

# calculates x and y variables used in modeling of adjusted close returns
class xy:
    def __init__(self,date,adj):
        self.date = date
        self.adj = adj

    # log returns of adj close price
    def log_ret(self,x):
        adj = self.adj
        log = pd.DataFrame([])
        for i in x:
            loc = adj.index.get_loc(self.date)
            adj_date = adj.iloc[loc]

            if i > adj.iloc[0:loc].shape[0]:
                window = adj[adj.index < self.date].iloc[0]
            else:
                window = adj[adj.index < self.date].iloc[-i]

            loc1 = adj.index.get_loc(window.name)
            adj_1 = adj.iloc[loc1]
            adj_log = np.log(adj_date/adj_1)
            log = pd.concat([log,adj_log], axis=1)

        header = list(map(str,x))
        y_head = []
        for i in header:
            y_head = y_head + ['y' + i]

        log.columns = y_head
        return(log)

    # moving average over specified period of days
    def move_avg(self,x):
        adj = self.adj
        date = self.date
        ma = pd.DataFrame([])
        for i in x:
            window = adj[adj.index < date].iloc[-1]
            loc1 = adj.index.get_loc(window.name)
            if i > adj.iloc[0:loc1].shape[0]:
                window2 = adj[adj.index < date].iloc[0]
            else:
                window2 = adj[adj.index < date].iloc[-i]

            loc2 = adj.index.get_loc(window2.name)
            adj_range = adj.iloc[loc2:loc1+1]
            adj_mean = adj_range.mean()
            ma = pd.concat([ma,adj_mean], axis=1)

        header = list(map(str,x))
        ma_head = []
        for i in header:
            ma_head = ma_head + ['ma' + i]

        ma.columns = ma_head
        return(ma)

    # log returns lagged by one day from specified date
    def lag_log_ret(self,x):
        adj = self.adj
        date = self.date
        log = pd.DataFrame([])
        for i in x:
            window = adj[adj.index < date].iloc[-1]
            loc = adj.index.get_loc(window.name)
            adj_date = adj.iloc[loc]

            if i > adj.iloc[0:loc].shape[0]:
                window2 = adj[adj.index < self.date].iloc[0]
            else:
                window2 = adj[adj.index < self.date].iloc[-i]

            loc1 = adj.index.get_loc(window2.name)
            adj_1 = adj.iloc[loc1]
            adj_log = np.log(adj_date/adj_1)
            log = pd.concat([log,adj_log], axis=1)

        header = list(map(str,x))
        pa = []
        for i in header:
            pa = pa + ['pa' + i]

        log.columns = pa
        return(log)




###### main code ######
# data reader variables
csv1 = 'tickers_nasd.csv'
csv2 = 'tickers_nyse.csv'
min_cap = 500*(10**6)
source = 'yahoo'
start_date = '2000-01-01'
end_date = '2017-11-17'

# read tickers from csv
# pull price date from yahoo api
nasd = reader(csv1,min_cap)
nyse = reader(csv2,min_cap)
nasd.csvr()
nyse.csvr()
ticker1 = nasd.tickers()
ticker2 = nyse.tickers()
ticker = combine_tickers(ticker1,ticker2)
yahoo = api(ticker,source,start_date,end_date)
# yahoo.api_save() # gets the api data from yahoo finance
file = yahoo.api_read()

# date list
# pulls adjusted close price from api data panel
d = ['2016-06-01','2017-07-03']
length = 60
adj = file.loc['Adj Close']

# distances in log, average and lagged log
log_x = [1,5,22]
ma_x = [5,22,200]
pa_x = [5,22,68]

#iterates for each desired date
for date in d:
    # bins
    dfcoef5 = pd.DataFrame([])
    dfcoef1 = pd.DataFrame([])
    dfcoef22 = pd.DataFrame([])
    dfp5 = pd.DataFrame([])
    dfp1 = pd.DataFrame([])
    dfp22 = pd.DataFrame([])

    # getting dates
    loc = adj.index.get_loc(date)
    adj1 = adj[loc:loc+length]
    adj1 = pd.DataFrame.transpose(adj1)
    dates = list(adj1.columns.values)

    # for loop through all dates
    # executes x and y variables of classes
    for time in dates:
        t = str(time)
        t = t.split('T')[0]
        stats = xy(t,adj)
        log_n = stats.log_ret(log_x)
        ma_n = stats.move_avg(ma_x)
        pa_n = stats.lag_log_ret(pa_x)
        ma_pa = pd.concat([pa_n,ma_n], axis=1)
        # for loop through each log return
        for yh in list(log_n):
            x = ma_pa
            y = log_n[yh]
            merge = pd.concat([x,y], axis=1).dropna(axis=0, how='any')
            mergen = merge.drop(yh, axis=1)
            mergen = sm.add_constant(mergen)
            est = sm.OLS(merge[yh],mergen).fit()
            coef = est.params
            p_val = est.pvalues
            # specifies which bin to store coefficients and pvalues in
            if yh == list(log_n)[0]:
                dfcoef1 = pd.concat([dfcoef1,coef],axis=1)
                dfp1 = pd.concat([dfp1,p_val],axis=1)
            elif yh == list(log_n)[1]:
                dfcoef5 = pd.concat([dfcoef5,coef],axis=1)
                dfp5 = pd.concat([dfp5,p_val],axis=1)
            elif yh == list(log_n)[2]:
                dfcoef22 = pd.concat([dfcoef22,coef],axis=1)
                dfp22 = pd.concat([dfp22,p_val],axis=1)

    # transposes bins, takes average of values
    df1 = dfcoef1.transpose().mean()
    df5 = dfcoef5.transpose().mean()
    df22 = dfcoef22.transpose().mean()
    dfstd1 = dfcoef1.transpose().std()
    dfstd5 = dfcoef5.transpose().std()
    dfstd22 = dfcoef22.transpose().std()
    dfp1 = dfp1.transpose().mean()
    dfp5 = dfp5.transpose().mean()
    dfp22 = dfp22.transpose().mean()

    # labels for variables in csv
    l0 = list(log_n)[0]
    l1 = list(log_n)[1]
    l2 = list(log_n)[2]
    s = ' std dev'
    p = ' p_val'

    # concatinates values into main variable dataframe
    # renames columns and outputs data frame to csv with the date as the name
    main = pd.concat([df1,df5,df22,dfstd1,dfstd5,dfstd22,dfp1,dfp5,dfp22],axis=1)
    main.columns = [l0,l1,l2,l0+s,l1+s,l2+s,l0+p,l1+p,l2+p]
    main.to_csv(date+'.csv')
