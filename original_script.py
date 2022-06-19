from operator import index
from textwrap import indent
import time
import requests
import json
import pprint
import pandas as pd


# page number variable to be updated as loop moves through results by the 10000
page_num = 1
# array of month days, index being months
months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# query constructors for date_query
opened = '{'
closed = '}'
date_contructor_1 = '"_and":['
date_contructor_2 = '"_gte":'
date_contructor_3 = ','
date_contructor_4 = '"_lte":'
date_contructor_5 = ']'

# setting query for the Options component of API get request
option_values =  f'"page": {page_num}, "per_page": 10000'
options_query = (opened+option_values+closed)

df=pd.DataFrame()
# df = pd.DataFrame()
# loop over years we wish to examine
for year in range(1980, 2022):
    # loop over array of months, with value being days and index being month
    for index, days in enumerate(months):
            # if month is less than 10 there is no leading 0, so we need to reformat single digit months to double
            if index < 9:
                # add 1 to index as starting index is 0 (and Jan is 1), then convert the 0 and the 1 to string and concat to result in "01"
                index = str(0) + str(index + 1)
            else:
                # if above 9, no need to add a 0, thus convert to string and add 1
                index = str(index + 1)
            page_num = 1
            count = 10000
            # convert year integer to string before we f-string in gte_date_values and lte_date_values
            year = str(year)
            # convert days integer to string before we f-string in gte_date_values and lte_date_values
            days = str(days)
            # variable to store greater than date parameter. updated by our for loop as we iterate over every month and year. e.g. "1980-01-01", "1980-02-01"..."2021-12-01"
            gte_date_values= f'"patent_date":"{year}-{index}-01"'
            # variable to store less than date parameter. updated by our for loop accessing year and month array. e.g. "1980-01-31", "1980-02-28", "2021-12-31"
            lte_date_values = f'"patent_date":"{year}-{index}-{days}"'
            # biggest meme construction of our date query component to avoide using {} brackets which would ruin the fstring url varibale below
            date_query = (opened+date_contructor_1+opened+date_contructor_2+opened+gte_date_values+closed+closed+date_contructor_3+opened+date_contructor_4+opened+lte_date_values+closed+closed+date_contructor_5+closed)        
            while count == 10000:
                values =  f'"page": {page_num}, "per_page": 10000'
                options_query = (opened+values+closed)
                url = f'https://api.patentsview.org/patents/query?q={date_query}&f=["patent_id", "patent_number", "patent_title", "patent_date", "patent_type", "patent_num_us_patent_citations", "inventor_first_name", "inventor_last_name", "inventor_longitude", "inventor_latitude", "inventor_city", "inventor_state"]&o={options_query}'# send get request to website
                response = requests.get(url=url)
                # store response object as python dicitonary
                response_dict = response.json()               
                # variable to store the count of patents per repsonse, i.e. count of patent applications per month
                count = response_dict["count"]
                # print count of patent applicaitons by month
                print(f'Page {page_num} of patent registrations in {gte_date_values[15:25]}: {count}')
                # access 'patents' key which returns list of dictionaries, where individual patents are dictionaries
                data = response_dict['patents']
                # update our dataframe we earlier initialised with the current months data,
                # df = df.append(data, ignore_index=True)
                df=df.append(data)
                # add page
                page_num+=1