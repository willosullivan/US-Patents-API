import json
import requests
import nest_asyncio

from typing import Union

from aiohttp import ClientSession

print('I will prepare `api_utils.py`')


# NOTE: This is necessary for Jupyter notebook
# because Jupyter notebook already starts an event loop
nest_asyncio.apply()


def get_patents(url: str) -> dict:
    print('Getting patents...')
    response = requests.get(url)
    return response.json()


async def async_get_patents(url: str) -> dict:
    print('Getting patents...')
    http_session = ClientSession()

    async with http_session.get(url) as response:
        response_json = await response.json()

    await http_session.close()

    return response_json


def prepare_date_query(
    year: Union[str, int],
    month: Union[str, int],
    days: Union[str, int],
) -> str:
    #  if type(month) == int:
    if isinstance(month, int):
        month = str(month).zfill(2)

    # variable to store greater than date parameter. updated by our for
    # loop as we iterate over every month and year.
    # e.g. "1980-01-01", "1980-02-01"..."2021-12-01"
    gte_date_values = f'{year}-{month}-01'
    # variable to store less than date parameter. updated by our for loop
    # accessing year and month array.
    # e.g. "1980-01-31", "1980-02-28", "2021-12-31"
    lte_date_values = f'{year}-{month}-{days}'
    # biggest meme construction of our date query component to avoide
    # using {} brackets which would ruin the fstring url varibale below
    date_query = {
        "_and": [
            {
                "_gte": {
                    "patent_date": gte_date_values
                }
            },
            {
                "_lte": {
                    "patent_date": lte_date_values
                }
            }
        ]
    }
    return json.dumps(date_query)


def prepare_options_query(page_num: int) -> str:
    options_query = {
        'page': page_num,
        'per_page': 10000,
    }
    return json.dumps(options_query)


def get_api(
    url: str,
    date_query_str: str,
    f_parameter_str: str,
    options_query_str: str,
) -> dict:
    response = requests.get(
        url=url,
        params={
            'q': date_query_str,
            'f': f_parameter_str,
            'o': options_query_str,
        }
    )
    # store response object as python dicitonary
    response_dict = response.json()
    # variable to store the count of patents per repsonse,
    # i.e. count of patent applications per month
    return response_dict


async def async_get_api(
    url: str,
    date_query_str: str,
    f_parameter_str: str,
    options_query_str: str,
) -> dict:

    http_session = ClientSession()
    async with http_session.get(
            url=url,
            params={
                'q': date_query_str,
                'f': f_parameter_str,
                'o': options_query_str,
            }
    ) as response:
        # store response object as python dicitonary
        response_dict = await response.json()
        # variable to store the count of patents per repsonse,
        # i.e. count of patent applications per month
    await http_session.close()

    return response_dict
