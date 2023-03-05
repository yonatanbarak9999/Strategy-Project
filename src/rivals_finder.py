"""
Author: Yonatan Barak
Date: 05/3/2023
"""
# ------ Import ------ #
import bs4
import os
import requests
from typing import List

import common

# ------ Consts ------ #

YAHOO_FINANCE_URL = 'https://finance.yahoo.com/'

RIVALS_SECTION = 'similar-by-symbol'


# ------ Functions ------ #

def get_rivals(url: str) -> List[str]:
    """
    Get all rivals from company page.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError

    tags = bs4.BeautifulSoup(response.text, 'html.parser')

    rivals: List[str] = []
    rivals_section = tags.select(f'section[id="{RIVALS_SECTION}"]')
    filtered_tags = bs4.BeautifulSoup(str(*rivals_section), 'html.parser')
    rivals_table = filtered_tags.select(
        'tr[class="dt-row Pos(r) Bgc($hoverBgColor):h BdB Bdbc($seperatorColor) H(44px)"]')

    try:
        while True:
            table_cell = rivals_table.pop()
            cell_tag = bs4.BeautifulSoup(str(table_cell), 'html.parser').p
            rivals.append(cell_tag.string)
    except IndexError:
        pass

    return rivals



