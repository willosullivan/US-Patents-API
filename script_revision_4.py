import asyncio

from patents_view_api.constants import months, f_parameter_str
from patents_view_api.file_storage import store_data
from patents_view_api.api_utils import (
    async_get_api,
    prepare_date_query,
    prepare_options_query,
)


async def main():
    # df = pd.DataFrame()
    # loop over years we wish to examine
    tasks = []
    for year in range(1980, 1981):
        # loop over array of months,
        # with value being days and index being month
        for index, days in enumerate(months):
            # convert the index into index + 1 and pad `0` until it has
            # 2 characters
            page_num = 1
            count = 10000

            date_query_str = prepare_date_query(
                year=year,
                month=index+1,
                days=days,
            )

            options_query_str = prepare_options_query(
                page_num=page_num
            )

            task = asyncio.ensure_future(
                async_get_api(
                    url='https://api.patentsview.org/patents/query',
                    date_query_str=date_query_str,
                    f_parameter_str=f_parameter_str,
                    options_query_str=options_query_str,
                )
            )
            tasks.append(task)

    for task in asyncio.as_completed(tasks):
        response_dict = await task

        count = response_dict["count"]
        # print count of patent applicaitons by month
        print(
            f'Page {page_num} of patent registrations in '
            f'{year}-{index+1}-01: {count}'
        )

        # access 'patents' key which returns list of dictionaries,
        # where individual patents are dictionaries
        data = response_dict['patents']
        # update our dataframe we earlier initialised with the current
        # months data,
        # df = df.append(data, ignore_index=True)
        store_data(data)

        # add page
        # page_num += 1

asyncio.run(main())
