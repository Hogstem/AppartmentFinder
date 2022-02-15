# ! python3
import urllib.parse
from pathlib import Path
from typing import Dict, Iterable, Union, Set

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook


def result_gen(url: str, max: int) -> Iterable[Dict[str, str]]:
    soup = BeautifulSoup(requests.get(url).content, 'lxml')

    i = 0  # used to keep track of how many results have been returned
    while True:
        # see the below links for information about the CSS selectors used in soup.select(...)
        # https://www.w3schools.com/csSref/sel_id.asp
        # https://www.w3schools.com/cssref/sel_class.asp
        for res in soup.select('#search-results li.result-row div.result-info'):
            posted = res.select_one('time.result-date')
            link = res.select_one('h3 a')
            price = res.select_one('span.result-price')
            location = res.select_one('span.result-hood')

            i += 1
            if i > max:
                break  # break the for loop if more than the max number of results have been returned

            yield {
                'name': link.text,
                'date': posted.text,
                'link': link['href'],
                'price': int(price.text.replace('$', '').replace(',', '')),
                'location': location.text
            }

        if i > max:
            break  # might also need to break the while loop

        try:  # try to keep getting the next page, and break the while loop if any errors happen
            # https://www.w3schools.com/cssref/sel_attr_begin.asp
            next_page_link = soup.select_one('a[title^=next]')

            next_url = urllib.parse.urlunsplit(
                # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit
                urllib.parse.urlsplit(url)._replace(path=next_page_link['href'])
            )

            print(f'Getting next page: {next_url}, {i} results so far')
            soup = BeautifulSoup(requests.get(next_url).content, 'lxml')
        except Exception as e:
            break


def save_results(path: Union[str, Path], results: Iterable[Dict]):
    path = Path(path) if not isinstance(path, Path) else path

    book = load_workbook(filename=str(path)) if path.exists() else Workbook()
    sheet = book.worksheets[0]

    if sheet.max_row <= 1:
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

    for i, res in enumerate(results):
        print(f'Saving ${res["price"]:,} - {res["name"]}')
        first_free_row = sheet.max_row + 1
        sheet.cell(row=first_free_row, column=1).value = res['name']
        sheet.cell(row=first_free_row, column=2).value = res['price']
        sheet.cell(row=first_free_row, column=3).value = res['link']
        sheet.cell(row=first_free_row, column=4).value = res['location']
        sheet.cell(row=first_free_row, column=5).value = res['date']

    book.save(filename=str(path))


def load_previous_results(path: Union[str, Path]) -> Set:
    if path.exists():
        prev_results = load_workbook(
            filename=str(path),
            read_only=True,
            data_only=True
        ).worksheets[0]

        return set(
            val
            # https://openpyxl.readthedocs.io/en/stable/api/openpyxl.worksheet.worksheet.html#openpyxl.worksheet.worksheet.Worksheet.iter_rows
            for val in prev_results.iter_rows(
                min_row=2, max_row=prev_results.max_row,
                min_col=3, max_col=3,
                values_only=True
            )
        )
    else:
        return set()


# if the date of the posting is todays date it will notify your desktop
# if str(res['date']) == today.strftime('%b %d'):
#     # https://github.com/ms7m/notify-py#usage
#     notification = Notify()
#     notification.title = res['name']
#     notification.message = f"{res['link']}\n{res['price']}"
#     notification.send()

# https://docs.python.org/3/library/__main__.html#idiomatic-usage
# https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == '__main__':
    # needs to have a urls.txt file in the same folder. The file should have 1 URL per line
    URL_LIST = Path('urls.txt').open('r').readlines()

    RESULTS = Path('Apartments.xlsx')

    prev_results = load_previous_results(RESULTS)

    save_results(
        path=RESULTS,
        results=(
            result
            for url in URL_LIST
            for result in result_gen(url, max=100)
            if result['link'] not in prev_results
        )
    )
