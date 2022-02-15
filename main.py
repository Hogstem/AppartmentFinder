# This program can be turned into a .bat file and run once or multiple times a day with task scheduler to send you a desktop notification when a new apartment is available

from datetime import date

# ! python3
import requests
from bs4 import BeautifulSoup
from notifypy import Notify
from openpyxl import Workbook as book

filename = "Apartment.xlsx"  # This creates the excel spreadsheet each time
workbook = book()
sheet = workbook.active
c = 0  # this is a counter for looping through the URL's in the list
li = []  # records links to rentals so that no repeats come up
URL = ['Enter the craigslist URL for the area you are in, make sure the max apartment price is at at least 700$']
Lis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U']
today = date.today()
o = 1


def result_gen(url: str):
    soup = BeautifulSoup(
        requests.get(url).content,
        'lxml'
    )
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


for url in URL_LIST:  # This cycles through the URL's if you have more than one
    for i, res in enumerate(result_gen(url)):
        if res['link'] not in li:
            if res['location'] is not None:
                if 10 <= res['price'] <= 1500:

                    li.append(res['link'])

                    sheet['A1'] = 'Item Name'
                    sheet['B1'] = 'Price'
                    sheet['C1'] = 'Link'
                    sheet['D1'] = 'Location'
                    sheet['E1'] = 'Posted Date'

                    sheet.column_dimensions['A'].width = 63
                    sheet.column_dimensions['C'].width = 89
                    sheet.column_dimensions['D'].width = 29

                    sheet[f'A{i}'] = res['name']
                    sheet[f'B{i}'] = res['price']
                    sheet[f'C{i}'] = res['link']
                    sheet[f'D{i}'] = res['location']
                    sheet[f'E{i}'] = res['date']

                    workbook.save(filename=filename)
                    # if the date of the posting is todays date it will notify your desktop

                    if str(res['date']) == today.strftime('%b %d'):
                        # https://github.com/ms7m/notify-py#usage
                        notification = Notify()
                        notification.title = res['name']
                        notification.message = f"{res['link']}\n{res['price']}"
                        notification.send()
