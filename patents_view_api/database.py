"""

4 building blocks when connecting to the database
- database (configurations)
    - This module contains the database configurations, including
        the connection configurations
- setup
    - This module contains the initialization of the database.
        This can also contain the code to manage the "migration" scripts
- models
    - This module contains the "classes" that are used to declare the
        SQL tables as Python Classes
- queries
    - This module contains all SQL statements that retrieves (or stores) data
        from (or to) the database.

"""


from typing import List
import psycopg2

from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import environ
from sqlalchemy.orm import Session

import urllib


load_dotenv()  # take environment variables from .env.

database_host = environ.get('DB_HOST')
database_name = environ.get('DB_NAME')
database_username = environ.get('DB_USERNAME')
database_password = environ.get('DB_PASSWORD')


engine = create_engine(
    f'postgresql://{database_username}:'
    # Escape the password to allow special characters
    f'{urllib.parse.quote(database_password)}'
    f'@{database_host}:5432/{database_name}'
)


def initialize_connection(func, *args, **kwargs):
    """
    A decorator for functions that need to connect to the database

    The functions should be able to receive a variable named `cur`
    """
    def wrapper(*args, **kwargs):
        """
        Prepares the database connection for the function
        """
        function_call_result = None
        conn = None
        try:
            if 'cur' in kwargs:
                cur = kwargs.pop('cur', None)
            else:
                conn = psycopg2.connect(
                    host="localhost",
                    database="docker",
                    user="docker",
                    password="docker"
                )

                cur = conn.cursor()

            function_call_result = func(cur=cur, *args, **kwargs)

            # Saves whatever was changed during the function call
            if conn:
                conn.commit()
        finally:
            # Close the connection to free up resources from the database
            if conn:
                conn.close()
        return function_call_result
    return wrapper


def initialize_sqlalchemy_connection(func, *args, **kwargs):
    """
    A decorator for functions that need to connect to the database

    The functions should be able to receive a variable named `cur`
    """
    def wrapper(*args, **kwargs):
        """
        Prepares the database connection for the function
        """
        if 'session' in kwargs:
            session = kwargs.pop('session', None)
            function_call_result = func(session=session, *args, **kwargs)
        else:
            with Session(engine) as session:
                function_call_result = func(session=session, *args, **kwargs)
        return function_call_result
    return wrapper


@initialize_connection
def store_patents(patents: List[dict], cur):
    """
        `patents: List[dict]` suggests that `patents` is a list of dictionaries

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
    for patent in patents:
        # Cleans the title to avoid SQL injection via single quotes (')
        patent['patent_title'] = patent['patent_title'].replace("'", "''")
        # print(patent['patent_title'])
        cur.execute(
            f'''
            INSERT INTO patents (patent_id, patent_title)
            VALUES (
                '{patent['patent_id']}',
                '{patent['patent_title']}'
            )
            ON CONFLICT(patent_id)
            DO
                UPDATE SET patent_title='{patent['patent_title']}'
            '''
        )

        if 'inventors' in patent:
            store_inventors(patent['inventors'], cur=cur)
            for inventor in patent['inventors']:
                cur.execute(
                    f'''
                    INSERT INTO inventor_patent_mapping (id, patent_id, inventor_key_id)
                    VALUES (
                        '{patent['patent_id']};{inventor['inventor_key_id']}',
                        '{patent['patent_id']}',
                        '{inventor['inventor_key_id']}'
                    )
                    ON CONFLICT(id)
                    DO NOTHING
                    '''
                )


def clean_sql_string(data: str) -> str:
    if data:
        return data.replace("'", "''")
    elif data is None:  # Empty data in Python
        return 'null'  # Empty data in SQL

    return ''


@initialize_connection
def store_inventors(inventors: List[dict], cur):
    """
        `inventors: List[dict]` suggests that `inventors` is a list of
        dictionaries

        inventors:
        [
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
    """
    for inventor in inventors:
        for key in (
            'inventor_first_name',
            'inventor_last_name',
            'inventor_city',
            'inventor_state',
            'inventor_longitude',
            'inventor_latitude',
        ):
            inventor[key] = clean_sql_string(inventor[key])

        # print(patent['patent_title'])
        cur.execute(
            f'''
            INSERT INTO inventors (key_id, first_name, last_name, location_longitude, location_latitude, location_city, location_state)
            VALUES (
                '{inventor['inventor_key_id']}',
                '{inventor['inventor_first_name']}',
                '{inventor['inventor_last_name']}',
                {inventor['inventor_longitude']},
                {inventor['inventor_latitude']},
                '{inventor['inventor_city']}',
                '{inventor['inventor_state']}'
            )
            ON CONFLICT(key_id)
            DO
                UPDATE SET first_name='{inventor['inventor_first_name']}',
                    last_name='{inventor['inventor_last_name']}',
                    location_longitude={inventor['inventor_longitude']},
                    location_latitude={inventor['inventor_latitude']},
                    location_city='{inventor['inventor_city']}',
                    location_state='{inventor['inventor_state']}'
            '''
        )


@initialize_connection
def init_database(cur):
    """
    Initializes the database by creating the `inventors` and `patents`
    table if they do not exist

    It will also contain the code to update the tables as necessary
    """
    print('Initializing the tables')
    print('Initializing `inventors`')
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS inventors (
            key_id VARCHAR PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR NOT NULL,
            location_city VARCHAR NOT NULL,
            location_state VARCHAR NOT NULL,
            location_longitude FLOAT,
            location_latitude FLOAT
        );
        '''
    )

    print('Initializing `patents`')
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS patents (
            patent_id VARCHAR PRIMARY KEY,
            patent_title VARCHAR NOT NULL
        );
        '''
    )

    print('Initializing `inventor_patent_mapping`')
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS inventor_patent_mapping (
            id VARCHAR PRIMARY KEY,
            patent_id VARCHAR NOT NULL,
            inventor_key_id VARCHAR NOT NULL,
            CONSTRAINT patent_id_fk
                FOREIGN KEY(patent_id)
                REFERENCES patents(patent_id),
            CONSTRAINT inventor_key_id_fk
                FOREIGN KEY(inventor_key_id)
                REFERENCES inventors(key_id)
        );
        '''
    )

    # TODO: Update the table definitions here as necessary like adding
    # more columns


@initialize_connection
def store_patent(patent: dict, cur):
    """
        `patent: dict` suggests that `patent` is a dictionary

        patent:
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
        }
    """
    # Cleans the title to avoid SQL injection via single quotes (')
    patent['patent_title'] = patent['patent_title'].replace("'", "''")
    print(patent['patent_title'])
    cur.execute(
        f'''
        INSERT INTO patents (patent_id, patent_title)
        VALUES (
            '{patent['patent_id']}',
            '{patent['patent_title']}');
        '''
    )
