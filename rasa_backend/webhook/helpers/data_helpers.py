import re

import lxml.html as lh
import requests
from cachetools import cached, TTLCache
from googletrans import Translator
from webhook.helpers.date_helpers import to_date

translator = Translator()

@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def crawler():
    url = 'https://www.worldometers.info/coronavirus/#countries'
    # Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    # Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    # Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    # Parse the last update time
    last_updated = re.findall(r'Last updated:.+? GMT', doc.text_content())[0]
    last_updated = last_updated.strip('Last updated:')
    last_updated = to_date(last_updated)

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

            if i in range(1, 6) and i not in [2, 4]:
                data = ''.join(c for c in data if c.isdigit())
                if data:
                    data = int(data)
                else:
                    data = 0
            # Append the data to the empty list of the i'th column
            col[i][1].append(data)
            # Increment i for the next column
            i += 1
    return col, last_updated


def generate_all_message(col, i):
    name, total, new, death, new_death, recover = [col[j][1][i] for j in range(0, 6)]
    name = translator.translate(name, dest='vi').text
    new = new if new else "+0"
    new_death = new_death if new_death else "+0"
    return "Tại {} đã có {} ca nhiễm ({} ca), tử vong {} ca ({} ca), chữa khỏi {} ca\n".format(name, total, new, death, new_death,
                                                                                 recover)

def get_data():
    col, last_updated = crawler()
    n = 10
    msg = "Top {} nơi có tình hình dịch nguy hiểm nhất.\n\n".format(n)
    for i in range(n):
        msg += generate_all_message(col, i)
    msg += "\nCập nhật mới nhất vào {}".format(last_updated)
    return msg


def handle_data(intent):
    try:
        intent_map = {
            'ask_death': 'deaths',
            'ask_resolve': 'recovered',
            'ask_confirm': 'confirmed',
            'ask_all': 'all',
            'fallback': 'fallback'
        }
        if intent_map[intent] in ["deaths", "recovered", "confirmed", 'all']:
            return get_data()
        # When fallback
        return "Chatbot chưa xử lý được nội dung bạn nói."
    except:
        return "Đã có lỗi xảy ra trong khi cập nhật dữ liệu. Bạn vui lòng thử lại sau"

print(handle_data('ask_all'))