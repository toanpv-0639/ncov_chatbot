import pickle
import re

import lxml.html as lh
import requests
from dateutil.parser import parse
from dateutil import tz

def to_date(string, fuzzy=False):
    try:
        VN_TZ = tz.gettz('Asia/Ho_Chi_Minh')
        UTC = tz.gettz('UTC')
        date = parse(string, fuzzy=fuzzy).replace(tzinfo=UTC)
        return date.astimezone(VN_TZ)
    except ValueError:
        return ""

url = 'https://www.worldometers.info/coronavirus/#countries'

# Create a handle, page, to handle the contents of the website
page = requests.get(url)
# Store the contents of the website under doc
doc = lh.fromstring(page.content)

# Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')

last_updated = re.findall(r'Last updated:.+? GMT', doc.text_content())[0]
last_updated = last_updated.strip('Last updated:')

col = []
i = 0

# Insert name of regions
for t in tr_elements[0]:
    i += 1
    name = t.text_content()
    col.append((name, []))

# Since out first row is the header, data is stored on the second row onwards
for j in range(1, len(tr_elements)):
    # T is our j'th row
    T = tr_elements[j]

    # If row is not of size 8, the //tr data is not from our table
    if len(T) != 8:
        break
    # i is the index of our column
    i = 0
    # Iterate through each element of the row

    for t in T.iterchildren():
        data = t.text_content().strip()

        if i in range(1, 6):
            data = ''.join(c for c in data if c.isdigit())
            if data:
                data = int(data)
            else:
                data = 0
        # Append the data to the empty list of the i'th column
        col[i][1].append(data)

        # Increment i for the next column
        i += 1
#
# pickle.dump(col, open('col.pk', 'wb'))
# col = pickle.load(open('col.pk', 'rb'))

def summary(col, region_name='All'):
    try:
        if region_name == 'All':
            sum_case = lambda k: sum([int(c) for c in col[k][1]])
        else:
            region_index = col[0][1].index(region_name)
            sum_case = lambda k: int(col[k][1][region_index])
        total_case = sum_case(1)
        new_case = sum_case(2)
        deaths_case = sum_case(3)
        new_deaths = sum_case(4)
        recover_case = sum_case(5)
        return total_case, new_case, deaths_case, new_deaths, recover_case
    except:
        return [0] * 5

total_case, new_case, deaths_case, new_deaths, recover_case = summary(col, region_name='China')
print(total_case, new_case, deaths_case, new_deaths, recover_case)