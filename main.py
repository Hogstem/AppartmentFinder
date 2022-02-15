# This program can be turned into a .bat file and run once or multiple times a day with task scheduler to send you a desktop notification when a new apartment is available

from datetime import date

# ! python3
import requests as r
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
for i in URL:  # This cycles through the URL's if you have more than one
    page = r.get(URL[c])
    c += 1

    soup = BeautifulSoup(page.content, 'lxml')  # parses the html

    for res in soup.select('#search-results li.result-row div.result-info'):
        posted = res.select_one('time.result-date')
        link = res.select_one('h3 a')
        price = res.select_one('span.result-price')
        location = res.select_one('span.result-hood')

        if link['href'] not in li:
            if location is not None:
                price_val = int(price.text.replace('$', '').replace(',', ''))
                if 10 <= price_val <= 1500:  # Keeps the apartments pulled in a range
                    li.append(link['href'])
                    o += 1  # This helps to move to the next line on the sheet with each new entry
                    sheet['A1'] = 'Item Name'
                    sheet['E1'] = 'Posted'
                    sheet['B1'] = 'Price'
                    sheet['C1'] = 'Link'
                    sheet['D1'] = 'Location'
                    sheet.column_dimensions['A'].width = 63
                    sheet.column_dimensions['C'].width = 89
                    sheet.column_dimensions['D'].width = 29
                    sheet['A' + str(o)] = str(link.text)
                    sheet['B' + str(o)] = str(price.text)
                    sheet['C' + str(o)] = str(link['href'])
                    sheet['D' + str(o)] = str(location.text)
                    sheet['E' + str(o)] = str(posted.text)
                    workbook.save(filename=filename)
                    # if the date of the posting is todays date it will notify your desktop

                    if str(posted.text) == today.strftime('%b %d'):
                        # https://github.com/ms7m/notify-py#usage
                        notification = Notify()
                        notification.title = link.text
                        notification.message = f"{link['href']}\n{price.text}"
                        notification.send()
