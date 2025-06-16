from datetime import datetime, date, timedelta
import pytz
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

url = 'https://www.nik.nl/sjabbattijden'

page = requests.get(url)

soup = BeautifulSoup(page.text, 'html.parser')

table = soup.find('table')

data = []

# tr = rij
# td = veld

for tr in table.find_all('tr')[1:]:
    tds = tr.find_all('td') # sla alle velden van een rij in tds op

    datum = tds[1].get_text(strip=True)
    tijd = tds[3]
    print(datum, tijd)

    try:
        parsed_date = datetime.strptime(datum, "%d-%b")
        parsed_date = parsed_date.replace(year=datetime.now().year)

        if parsed_date.weekday() == 5:
            data.append({'Datum': parsed_date.strftime('%Y-%m-%d'), 'Begin shabbat': tijd})
    except ValueError:
        print(datum)
        continue

df = pd.DataFrame(data)

print(df)