import re

import lxml.html as lh
import requests
from cachetools import cached, TTLCache
from googletrans import Translator

from webhook.helpers.date_helpers import to_date

translator = Translator()

maps = {
    "Diamond Princess": "Tàu Diamon Princess",
    "Italy": "Nước Ý",
    "Thailand": "Thái Lan",
    "Hong Kong": "Hồng Kông",
    "China": "Trung Quốc",
    "S. Korea": "Hàn Quốc",
    "Iran": "Iran",
    "France": "Pháp",
    "Germany": "Đức",
    "Spain": "Tây Ban Nha",
    "Japan": "Nhật Bản",
    "USA": "Hoa Kỳ",
    "Switzerland": "Thụy ĩ",
    "UK": "Anh",
    "Netherlands": "Hà Lan",
    "Belgium": "Bỉ",
    "Sweden": "Thụy Điển",
    "Norway": "Na Uy",
    "Singapore": "Singapore",
    "Austria": "Áo",
    "Malaysia": "Malaysia",
    "Bahrain": "Bahrain",
    "Australia": "Châu Úc",
    "Greece": "Hy lạp",
    "Kuwait": "Kuwait",
    "Canada": "Canada",
    "Iraq": "Iraq",
    "Iceland": "Nước Iceland",
    "Egypt": "Ai Cập",
    "Taiwan": "Đài Loan",
    "UAE": "UAE",
    "India": "Ấn Độ",
    "Lebanon": "Lebanon",
    "Denmark": "Đan mạch",
    "San Marino": "San Marino",
    "Czechia": "Cộng hòa Séc",
    "Israel": "Người israel",
    "Portugal": "Bồ Đào Nha",
    "Finland": "Phần Lan",
    "Vietnam": "Việt Nam Vô Địch",
    "Algeria": "Algeria",
    "Brazil": "Brazil",
    "Ireland": "Ireland",
    "Palestine": "Palestine",
    "Oman": "oman",
    "Russia": "Nga",
    "Ecuador": "Ecuador",
    "Georgia": "Georgia",
    "Romania": "romania",
    "Croatia": "Croatia",
    "Qatar": "Qatar",
    "Slovenia": "Slovenia",
    "Saudi Arabia": "Ả Rập Xê-út",
    "Macao": "Macao",
    "Estonia": "Estonia",
    "Argentina": "Argentina",
    "Azerbaijan": "Azerbaijan",
    "Mexico": "Mexico",
    "Chile": "Chile",
    "Philippines": "Philippines",
    "Belarus": "Belarus",
    "Indonesia": "Indonesia",
    "Pakistan": "Pakistan",
    "Peru": "Peru",
    "Poland": "Ba Lan",
    "New Zealand": "New Zealand",
    "Costa Rica": "Costa Rica",
    "French Guiana": "Guiana thuộc Pháp",
    "Hungary": "Hungary",
    "Afghanistan": "Afghanistan",
    "Senegal": "Senegal",
    "Bulgaria": "Bulgaria",
    "Luxembourg": "Luxembourg",
    "North Macedonia": "Bắc Macedonia",
    "Bosnia and Herzegovina": "Bosnia và Herzegovina",
    "Malta": "Malta",
    "Slovakia": "Slovakia",
    "South Africa": "Nam Phi",
    "Cambodia": "Campuchia",
    "Dominican Republic": "Cộng hoà Dominicana",
    "Morocco": "Morocco",
    "Cameroon": "Cameroon",
    "Faeroe Islands": "Quần đảo Faroe",
    "Maldives": "Maldives",
    "Andorra": "Andorra",
    "Armenia": "Armenia",
    "Jordan": "Jordan",
    "Latvia": "Latvia",
    "Lithuania": "nước Lithuania",
    "Monaco": "Monaco",
    "Nepal": "Nepal",
    "Nigeria": "Nigeria",
    "Sri Lanka": "Sri Lanka",
    "Tunisia": "Tunisia",
    "Ukraine": "Ukraina",
    "Bhutan": "Bhutan",
    "Colombia": "Colombia",
    "Gibraltar": "Gibraltar",
    "Vatican City": "Toà thánh Vatican",
    "Liechtenstein": "Liechtenstein",
    "Moldova": "Moldavia",
    "Paraguay": "Paraguay",
    "Serbia": "Serbia",
    "Togo": "Togo",
    "Total:": "Toàn bộ:"
}

@cached(cache=TTLCache(maxsize=10240, ttl=300))
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
        try:
            name = t.text_content()
            col.append((name, []))
        except Exception:
            pass
    # Since out first row is the header, data is stored on the second row onwards
    for j in range(1, len(tr_elements)):
        # T is our j'th row
        T = tr_elements[j]
        # i is the index of our column
        i = 0
        # Iterate through each element of the row
        for t in T.iterchildren():
            try:
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
            except Exception:
                pass
    return col, last_updated


def convert_name(name):
    if name in maps.keys():
        return maps[name]
    return translator.translate(name, dest='vi').text


def generate_all_message(col, i):
    name, total, new, death, new_death, active, recover = [col[j][1][i] for j in range(0, 7)]
    name = convert_name(name)
    new = new if new else "+0"
    new_death = new_death if new_death else "+0"
    return "{}: 😷 {} [{}], 💀 {} [{}], 💊 {}\n".format(name, total, new, death, new_death, recover)

def get_message_by_country(col, name):
    for i, c in enumerate(col):
        if c[0] == name:
            return generate_all_message(col, i)
    return 0

def get_data(top_k):
    col, last_updated = crawler()
    if top_k == -1:
        top_k = len(col[0][1])
    msg = "TOP {} NƠI CÓ DỊCH NGUY HIỂM NHẤT.\n\n".format(top_k)
    for i in range(top_k):
        msg += generate_all_message(col, i)
    msg += "=================:\n"
    msg += generate_all_message(col, col[0][1].index('Vietnam'))
    msg += "=================:\n"
    msg += generate_all_message(col, len(col[0][1]) - 1)
    msg += "\nCập nhật mới nhất vào {}".format(last_updated)
    return msg


def handle_data(intent, top_k):
    try:
        intent_map = {
            'ask_death': 'deaths',
            'ask_resolve': 'recovered',
            'ask_confirm': 'confirmed',
            'ask_all': 'all',
            'fallback': 'fallback'
        }
        if intent_map[intent] in ["deaths", "recovered", "confirmed", 'all']:
            return get_data(top_k)
        # When fallback
        return "Chatbot chưa xử lý được nội dung bạn nói."
    except:
        return "Đã có lỗi xảy ra trong khi cập nhật dữ liệu. Bạn vui lòng thử lại sau"


print(handle_data('ask_all', 20))

