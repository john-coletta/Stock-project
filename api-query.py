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

# API url (see http://100.26.29.52:5000/api/ui/)
api_options_url = 'http://100.26.29.52:5000/api/options/'
api_quotes_url = 'http://100.26.29.52:5000/api/quotes/'

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

aapl_options_df['pricedate'] = pd.to_datetime(aapl_options_df['pricedate'], unit='s')

aapl_options_df['ask'].hist()
aapl_options_df['strike'].hist()
aapl_options_df['lastprice'].hist()

aapl_price_df['pricedate'] = pd.to_datetime(aapl_price_df['pricedate'], unit='s')
aapl_price_df['regulardate'] = pd.to_datetime(aapl_price_df['regulardate'], unit='s')

aapl_price_df['pricedate'].head()

plt.plot(aapl_price_df['pricedate'], aapl_price_df['close'])

plt.plot(aapl_options_df['pricedate'], aapl_options_df['lastprice'])


