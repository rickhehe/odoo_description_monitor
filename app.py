#!C:\Users\rick.NETWORK\AppData\Local\Programs\Python\Python38-32\python.exe

import os
import re

import pandas as pd
import numpy as np

from query import get, run
from connections import live
from datetime_tricks import datetime_csv_suffix
from emailer import send_email_to

pd.options.display.max_columns = 29
pd.options.display.expand_frame_repr = False


OUTPUT_DIRECTORY = r'c:/backup/'

# get the old
def get_the_old(field, pat):

    sql = f'''
        select id
               , {field} {field}_old
          from product_template template
         where {field} ~* '{pat}'
    '''

    return get(sql, live)

def update_the_old(field, pat, replacement):

    sql = f'''
        update product_template template
           set {field} = regexp_replace(
                   {field}
                   , '{pat}'
                   , '{replacement}'
                   , 'i'
               )
         where {field} ~* '{pat}'
    '''

    run(sql, live)

def get_new(id_, field):
    
    sql = f'''
        select id, {field} {field}_new
          from product_template template
         where id = {id_}
    '''

    return get(sql, live)

def haha():

    for field,pr in fields.items():
        for pat, replacement in pr.items():

            original = get_the_old(
                field=field,
                pat=pat
            )

            if original.empty:
                return None

            update_the_old(
                field=field,
                pat=pat,
                replacement=replacement
            )
            
            new = pd.concat(
                get_new(id_=i, field=field)
                for i
                in original.id.unique()
            )

            df = original.merge(new, on='id')

            df.to_csv(
                os.path.join(
                    OUTPUT_DIRECTORY,
                    't_description',
                    datetime_csv_suffix('LR.csv')
                )
            )

pat_replacement = {
    # All tailing LHS/ RHS description to be ABBR.
    'left side(?: only)?\W*$': 'LHS',
    'right side(?: only)?\W*$': 'RHS',
}

fields = {
    'name': pat_replacement,
    'description_sale': pat_replacement
}

try:

    haha()
    send_email_to(
        subject='yay'
    )

except Exception as e:

    send_email_to(
        subject='ERROR t_description',
        content=e
    )
