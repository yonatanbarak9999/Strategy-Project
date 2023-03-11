"""
Author: Yonatan Barak
Date: 05/3/2023
"""
# ------ Import ------ #
import bs4
import os
import pandas as pd
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


def get_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    company_code = data['quotes'][0]['symbol']
    return company_code


def get_url(company: str) -> str:
    return 'https://finance.yahoo.com/quote/' + get_ticker(company)


def create_rivals_file():
    companies_with_rivals = pd.DataFrame(columns=(['company'] + [f'rival_{i}' for i in range(5)]))
    with open(os.path.join(common.ASSETS_PATH, 'companies.txt'), 'rt') as companies:
        for company in companies:
            try:
                url = get_url(company.replace("\n", ""))
            except Exception:
                company = company.replace("\n", "")
                print(f'Couldn\'t find {company}\'s url')
            else:
                try:
                    rivals = {f'rival_{i}': rival for i, rival in enumerate(get_rivals(url))}
                    rivals.update({'company': company})
                    df = pd.DataFrame([rivals])
                    companies_with_rivals = pd.concat([companies_with_rivals, df],
                                                      ignore_index=True)
                    company = company.replace("\n", "")
                    print(f'{company}\'s rivals: {rivals}')

                except Exception:
                    company = company.replace("\n", "")
                    print(f'Couldn\'t find {company}\'s rivals')

    companies_with_rivals.to_csv(os.path.join(common.ASSETS_PATH, 'rivals.csv'))


create_rivals_file()
