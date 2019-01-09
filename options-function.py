# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 12:10:29 2018

@author: johnb
"""

# Import necessary libraries
import pandas as pd
import numpy as np
import json
import requests
import matplotlib.pyplot as plt
import sys
from datetime import datetime

from Portfolio import Portfolio
from modelTools import modelTools as mt

# API url (see http://100.26.29.52:5000/api/ui/)
api_options_url = 'http://data.fanaleresearch.com/api/options/'
api_quotes_url = 'http://data.fanaleresearch.com/api/quotes/'

r = requests.get(api_options_url + 'all/AAPL')
r2 = requests.get(api_quotes_url + 'AAPL')

aapl_dict = json.loads(r.text)
aapl_price = json.loads(r2.text)

print(aapl_dict[1])
print(aapl_price[1])

aapl_options_df = pd.DataFrame(aapl_dict)
aapl_price_df = pd.DataFrame(aapl_price)

print(aapl_options_df.head())
print(aapl_options_df.columns)

aapl_options_df['pricedate'] = aapl_options_df['pricedate'].astype('float').astype('int64').apply(datetime.fromtimestamp)
aapl_options_df['expiry'] = aapl_options_df['expiry'].astype('int64').apply(datetime.fromtimestamp)# + pd.Timedelta(hours=16)

aapl_options_df['days_to_expiry'] = (aapl_options_df['expiry'] - aapl_options_df['pricedate']).dt.days

aapl_options_df[aapl_options_df['contractsymbol'] == 'AAPL190118C00145000'][['pricedate']]

print(aapl_options_df[['expiry','pricedate','days_to_expiry']].head(20))

aapl_options_df['calcprice'] = (aapl_options_df['ask'] + aapl_options_df['bid']) / 2

aapl_options_df['calcprice'] = np.where(aapl_options_df['calcprice'] == 0, aapl_options_df['lastprice'],aapl_options_df['calcprice'])
aapl_options_df['calcprice'].describe()

aapl_options_df['ask'].hist()
aapl_options_df['strike'].hist()
aapl_options_df['lastprice'].hist()

aapl_price_df['pricedate'] = pd.to_datetime(aapl_price_df['pricedate'], unit='s')
aapl_price_df['regulardate'] = pd.to_datetime(aapl_price_df['regulardate'], unit='s')

aapl_price_df['pricedate'].head()

plt.plot(aapl_price_df['pricedate'], aapl_price_df['close'])

plt.plot(aapl_options_df['pricedate'], aapl_options_df['lastprice'])

'''
myport = Portfolio.Portfolio()
mt.get_one_option('aapl',myport)

print(myport.holdings)

myport.returns()
myport.holdings['aapl']['returns']

i = 0
for stock in myport.holdings:
    print(myport.holdings[stock]['returns'])
    i += 1
    if i == 5:
        break
  '''  
print(aapl_options_df[aapl_options_df['contractsymbol'] == str(aapl_options_df['contractsymbol'].head()[0])]['pricedate'])

aapl_sorted = aapl_options_df.sort_values('pricedate')
aapl_grouped = aapl_sorted.groupby('contractsymbol')

aapl_grouped.groups


all_returns = pd.Series()
calc_returns = pd.Series()
for contract in aapl_grouped.groups.keys():
    returns = (aapl_grouped.get_group(contract)['lastprice'].shift(1) - aapl_grouped.get_group(contract)['lastprice'])/aapl_grouped.get_group(contract)['lastprice']
    #print(returns.index)
    calcs = (aapl_grouped.get_group(contract)['calcprice'].shift(1) - aapl_grouped.get_group(contract)['calcprice'])/aapl_grouped.get_group(contract)['calcprice']
    all_returns  = all_returns.append(returns)
    calc_returns = calc_returns.append(calcs)
    #print(all_returns.index)

all_returns.rename('returns',inplace=True)
calc_returns.rename('calc_returns',inplace=True)
aapl_joined = aapl_options_df.join(all_returns).join(calc_returns)

aapl_joined.describe()

aapl_joined['contractsymbol'].value_counts()

aapl_joined[aapl_joined['contractsymbol'] == 'AAPL190118C00145000'][['pricedate']].head(20)
aapl_joined[aapl_joined['optiontype'] == 'put'].mean()

def get_options(ticker):
    '''
    This function gets the option chain for a stock,
    puts it into a pandas dataframe, and calculates
    daily returns for each option, calculated returns,
    and days to expiration
    NOTE: the first occurance of each option has a 
    return of NaN
    '''
    
    # This is the API url for options
    options_url = 'http://data.fanaleresearch.com/api/options/'
    # Get the option chain for a stock (in json)
    r_ticker = requests.get(options_url + 'all/' + str(ticker))
    # Load the json into a dictionary and convert to a pandas dataframe
    ticker_dict = json.loads(r_ticker.text)
    ticker_df = pd.DataFrame(ticker_dict)
    
    # Create calculated price and convert dates from UNIX time to datetime
    ticker_df['calcprice'] = (ticker_df['ask'] + ticker_df['bid']) / 2
    ticker_df['pricedate'] = ticker_df['pricedate'].astype('float').astype('int64').apply(datetime.fromtimestamp)
    ticker_df['expiry'] = ticker_df['expiry'].astype('int64').apply(datetime.fromtimestamp)
    
    # Calculate days to expiry
    ticker_df['days_to_expiry'] = (ticker_df['expiry'] - ticker_df['pricedate']).dt.days
    # Make sure the calc price is never 0 (if it use just use the last price)
    ticker_df['calcprice'] = np.where(ticker_df['calcprice'] == 0, ticker_df['lastprice'], ticker_df['calcprice'])
    # Sort by the date so the subsequent grouping is sorted too
    ticker_sorted = ticker_df.sort_values('pricedate')
    # Group by contract
    ticker_grouped = ticker_sorted.groupby('contractsymbol')
    
    # Create empty series for returns
    ticker_returns = pd.Series()
    ticker_calc_returns = pd.Series()
    for contract in ticker_grouped.groups.keys():
        ''' This for loop calculates the true returns and calculated returns and
        then joins them to the dataframe
        '''
        sub_returns = (ticker_grouped.get_group(contract)['lastprice'].shift(1) - ticker_grouped.get_group(contract)['lastprice'])/ticker_grouped.get_group(contract)['lastprice']
        #print(returns.index)
        sub_calc = (ticker_grouped.get_group(contract)['calcprice'].shift(1) - ticker_grouped.get_group(contract)['calcprice'])/ticker_grouped.get_group(contract)['calcprice']
        ticker_returns  = ticker_returns.append(sub_returns)
        ticker_calc_returns = ticker_calc_returns.append(sub_calc)
        
        #print(all_returns.index)

    ticker_returns.rename('returns',inplace=True)
    ticker_calc_returns.rename('calc_returns',inplace=True)
    ticker_joined = ticker_df.join(ticker_returns).join(ticker_calc_returns)
    
    # A dataframe with the option chain information and the returns is the output
    return(ticker_joined)
        
IBM = get_options('IBM')

IBM['days_to_expiry']
IBM.head()    
IBM[IBM['optiontype'] == 'call'].groupby('contractsymbol').volume.mean()

IBM[IBM['contractsymbol'] == 'IBM181026C00116000'].pricedate

plt.scatter('strike','calc_returns', data=IBM[IBM['optiontype'] == 'put'].groupby('contractsymbol').mean())

weird = IBM[IBM['optiontype'] == 'put'].groupby('contractsymbol').mean().query('calc_returns >= 5').index.values

IBM[IBM['contractsymbol'] == weird[0]][['expiry','pricedate','lastprice', 'calc_returns']]
