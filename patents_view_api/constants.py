import json

# array of month days, index being months
months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

F_PARAMETER = [
    "patent_id",
    "patent_number",
    "patent_title",
    "patent_date",
    "patent_type",
    "patent_num_us_patent_citations",
    "inventor_first_name",
    "inventor_last_name",
    "inventor_longitude",
    "inventor_latitude",
    "inventor_city",
    "inventor_state"
]
f_parameter_str = json.dumps(F_PARAMETER)
