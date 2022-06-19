from .models import Inventor, InventorPatentMapping, Patent
from .database import initialize_sqlalchemy_connection
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.dialects.postgresql import insert


@initialize_sqlalchemy_connection
def count_inventors(session: Session):
    inventor_count = session.query(Inventor).count()
    return inventor_count


@initialize_sqlalchemy_connection
def get_inventor_patents(inventor_key_id: str, session: Session):
    results = session.query(
        Inventor, Patent
    ).where(
        Inventor.key_id == inventor_key_id
    ).join(
        InventorPatentMapping,
        InventorPatentMapping.inventor_key_id == Inventor.key_id
    ).join(
        Patent,
        InventorPatentMapping.patent_id == Patent.patent_id
    ).all()

    return results


@initialize_sqlalchemy_connection
def store_patents(patents: List[dict], session, commit=False):
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
        patent_stmt = insert(Patent).values(
            patent_id=patent['patent_id'],
            patent_title=patent['patent_title'],
        ).on_conflict_do_update(
            index_elements=[Patent.patent_id],
            set_={
                'patent_title': patent['patent_title']
            }
        )
        session.execute(patent_stmt)

        if 'inventors' in patent:
            store_inventors(patent['inventors'], session=session)
            for inventor in patent['inventors']:
                inv_patent_stmt = insert(InventorPatentMapping).values(
                    id=f"{patent['patent_id']};{inventor['inventor_key_id']}",
                    patent_id=patent['patent_id'],
                    inventor_key_id=inventor['inventor_key_id'],
                ).on_conflict_do_nothing(
                    index_elements=[InventorPatentMapping.id]
                )
                session.execute(inv_patent_stmt)

    if commit:
        session.commit()


def clean_sql_string(data: str) -> str:
    if data:
        return data.replace("'", "''")
    elif data is None:  # Empty data in Python
        return 'null'  # Empty data in SQL

    return ''


@initialize_sqlalchemy_connection
def store_inventors(inventors: List[dict], session, commit=False):
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
        # TODO: Change me once `location_state`` is nullable
        inventor_state = inventor["inventor_state"]
        if inventor_state is None:
            inventor_state = ''
        inventor_city = inventor["inventor_city"]
        if inventor_city is None:
            inventor_city = ''

        inventor_stmt = insert(Inventor).values(
            first_name=inventor["inventor_first_name"],
            last_name=inventor["inventor_last_name"],
            location_longitude=inventor["inventor_longitude"],
            location_latitude=inventor["inventor_latitude"],
            location_city=inventor_city,
            location_state=inventor_state,
            key_id=inventor["inventor_key_id"],
        ).on_conflict_do_update(
            index_elements=[Inventor.key_id],
            set_={
                'first_name': inventor["inventor_first_name"],
                'last_name': inventor["inventor_last_name"],
                'location_longitude': inventor["inventor_longitude"],
                'location_latitude': inventor["inventor_latitude"],
                'location_city': inventor_city,
                'location_state': inventor_state,
            }
        )
        session.execute(inventor_stmt)
    if commit:
        session.commit()
