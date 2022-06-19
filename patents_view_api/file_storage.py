from typing import List
from csv import DictWriter


def store_data(patents: List[dict]):
    """
        `data: dict` suggests that `data` is a dictionary

        patents:
        [
            {
                "patent_id": "4180867",
                "patent_number": "4180867",
                "patent_title": "Space enclosing member",
                "patent_date": "1980-01-01",
                "patent_type": "utility",
                "patent_num_us_patent_citations": "5",
                "inventors": [
                    {
                        "inventor_first_name": "Marcus L.",
                        "inventor_last_name": "Ridgeway, Jr.",
                        "inventor_longitude": "-97.3002",
                        "inventor_latitude": "31.2004",
                        "inventor_city": "Troy",
                        "inventor_state": "TX",
                        "inventor_key_id": "3286472"
                    }
                ]
            },
            ...
        ]
    """
    with open('patents.csv', 'w+') as patents_file:
        csv_writer = DictWriter(
            patents_file,
            fieldnames=patents[0].keys(),
        )
        csv_writer.writerows(patents)
