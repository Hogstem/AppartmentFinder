# ! python3

# This program can be turned into a .bat file and run once or multiple times a day with task scheduler to send you a desktop notification when a new apartment is available

from pathlib import Path
from typing import List, Dict, Iterable

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook


def result_gen(url: str = 'Apartment.xlsx') -> Iterable[Dict[str, str]]:
    soup = BeautifulSoup(requests.get(url).content, 'lxml')

    for res in soup.select('#search-results li.result-row div.result-info'):
        posted = res.select_one('time.result-date')
        link = res.select_one('h3 a')
        price = res.select_one('span.result-price')
        location = res.select_one('span.result-hood')

        yield {
            'name': link.text,
            'date': posted.text,
            'link': link['href'],
            'price': int(price.text.replace('$', '').replace(',', '')),
            'location': location.text
        }


def save_results(path: Path, results: List[Dict]):
    path = Path(path) if not isinstance(path, Path) else path

    if path.exists():
        book = load_workbook(filename=str(path))
    else:
        book = Workbook()
        sheet = book.worksheets[0]

        sheet.column_dimensions['A'].width = 63
        sheet.column_dimensions['C'].width = 89
        sheet.column_dimensions['D'].width = 29

        headers = [
            'Item Name',
            'Price',
            'Link',
            'Location',
            'Posted Date'
        ]

        for i, h in enumerate(headers):
            sheet.cell(row=1, column=i + 1).value = h

    sheet = book.worksheets[0]
    for i, res in enumerate(results):
        first_free_row = sheet.max_row + 1
        sheet.cell(row=first_free_row, column=1).value = res['name']
        sheet.cell(row=first_free_row, column=2).value = res['price']
        sheet.cell(row=first_free_row, column=3).value = res['link']
        sheet.cell(row=first_free_row, column=4).value = res['location']
        sheet.cell(row=first_free_row, column=5).value = res['date']

    book.save(filename=str(path))

# if the date of the posting is todays date it will notify your desktop
# if str(res['date']) == today.strftime('%b %d'):
#     # https://github.com/ms7m/notify-py#usage
#     notification = Notify()
#     notification.title = res['name']
#     notification.message = f"{res['link']}\n{res['price']}"
#     notification.send()

if __name__ == '__main__':
    URL_LIST = ['Enter the craigslist URL for the area you are in, make sure the max apartment price is at at least 700$']

    results = [
        result
        for url in URL_LIST
        for result in result_gen(url)
    ]

    print(f'Found {len(results)} listings')

    save_results('Apartment.xlsx', results)
