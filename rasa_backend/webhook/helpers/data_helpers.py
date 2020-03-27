import re

import lxml.html as lh
import requests
from cachetools import cached, TTLCache
from googletrans import Translator
from bs4 import BeautifulSoup
import pandas as pd

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
    "Switzerland": "Thụy Sĩ",
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
    "Israel": "Israel",
    "Portugal": "Bồ Đào Nha",
    "Finland": "Phần Lan",
    "Vietnam": "Việt Nam Vô Địch",
    "Algeria": "Algeria",
    "Brazil": "Brazil",
    "Ireland": "Ireland",
    "Palestine": "Palestine",
    "Oman": "Oman",
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

url = 'https://www.worldometers.info/coronavirus/#countries'

@cached(cache=TTLCache(maxsize=10240, ttl=300))
def crawler():
    # Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    # Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table', attrs={'id': 'main_table_countries_today'})
    # Convert to dataframe
    df = pd.read_html(str(table))[0]
    df = df.fillna(0)
    final_df = df.sort_values(by=['TotalCases'], ascending=False)
    final_df.set_index('Country,Other', inplace=True)
    # Parse the last update time
    last_updated = re.findall(r'Last updated:.+? GMT', doc.text_content())[0]
    last_updated = last_updated.strip('Last updated:')
    last_updated = to_date(last_updated)

    return final_df, last_updated


def convert_name(name):
    return maps.get(name, name)

def generate_one_message(row):
    new = row['NewCases']
    total = row['TotalCases']
    death = row['TotalDeaths']
    new_death = row['NewDeaths']
    recover = row['TotalRecovered']
    name = convert_name(row.name)
    death_ratio = round(death / total * 100, 2)
    recover_ratio = round(recover / total * 100, 2)
    return "{}: 😷 {} [{}], 💀 {} [{} {}%], 💊 {} [{}%]\n".format(name, int(total), new, int(death), new_death, death_ratio,
                                                                  int(recover), recover_ratio)


def get_data(top_k):
    col, last_updated = crawler()
    total = len(col) - 2
    if top_k == -1:
        top_k = total
    msg = "TOP {}/{} NƠI CÓ DỊCH NGUY HIỂM NHẤT.\n\n".format(top_k, total)
    for i in range(top_k):
        msg += generate_one_message(col.iloc[i + 1])
    msg += "=================:\n"
    msg += generate_one_message(col.loc['Vietnam'])
    msg += "=================:\n"
    msg += generate_one_message(col.loc['Total:'])
    msg += "\nCập nhật mới nhất vào {}".format(last_updated)
    msg += "\n\nNguồn tham khảo: {}".format(url)

    return msg


def handle_data(intent, top_k):
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
    # try:
    #     intent_map = {
    #         'ask_death': 'deaths',
    #         'ask_resolve': 'recovered',
    #         'ask_confirm': 'confirmed',
    #         'ask_all': 'all',
    #         'fallback': 'fallback'
    #     }
    #     if intent_map[intent] in ["deaths", "recovered", "confirmed", 'all']:
    #         return get_data(top_k)
    #     # When fallback
    #     return "Chatbot chưa xử lý được nội dung bạn nói."
    # except:
    #     return "Đã có lỗi xảy ra trong khi cập nhật dữ liệu. Bạn vui lòng thử lại sau"


print(handle_data('ask_all', 30))

