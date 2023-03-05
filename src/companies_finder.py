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

COMPANIES_WEBPAGE_PATH = 'https://www.climateaction100.org/whos-involved/companies'
PAGE_PATH = '/page/{page_number}/'
PAGES = 7

CARD_HEADER = '<h3 class="card-header-title">'
CARD_TAIL = '</h3>'

COMPANIES_FILE = 'companies.txt'


# ------ Functions ------ #

def get_page(page: int):
    """
    Get a certain page in the companies pages.
    """
    if page == 1:
        url = COMPANIES_WEBPAGE_PATH
    else:
        url = COMPANIES_WEBPAGE_PATH + PAGE_PATH.format(page_number=(page + 1))

    return requests.get(url)


def get_companies_from_cards(tags: bs4.BeautifulSoup) -> List[str]:
    """
    Get a list of companies from each page
    """
    companies: List[str] = []
    companies_raw = tags.select('h3[class="card-header-title"]')
    try:
        while True:
            company_raw = str(companies_raw.pop())
            company_raw = company_raw.replace(CARD_HEADER, '')
            company_raw = company_raw.replace(CARD_TAIL, '')
            company = company_raw. \
                replace('\t', ''). \
                replace('\n', ''). \
                replace('\r', '')

            companies.append(company)

    except IndexError:
        pass

    return companies[::-1]


def write_results(companies: List[str]):
    """
    Write results to assets directory.
    """
    common.create_assets_dir()
    results_path = os.path.join(common.ASSETS_PATH, COMPANIES_FILE)
    with open(results_path, 'wt') as companies_file:
        for company in companies:
            companies_file.write(company + '\n')


def get_companies():
    companies: List[str] = []

    for page in range(PAGES):
        print(f'Extracting companies names from page {page + 1}')
        response = get_page(page)
        if response.status_code != 200:
            print(f'Could not get page number {page + 1}')
            return

        companies += get_companies_from_cards(
            bs4.BeautifulSoup(response.text, 'html.parser'))

    print(f'Done! Writing results to assets directory.')
    write_results(companies)


get_companies()
