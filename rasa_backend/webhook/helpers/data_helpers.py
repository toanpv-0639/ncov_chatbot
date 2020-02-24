import re

import lxml.html as lh
import requests
from cachetools import cached, TTLCache
from webhook.helpers.date_helpers import to_date

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
    return col, last_updated


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


def get_data(category):
    col, last_updated = crawler()
    total_case, new_case, deaths_case, new_deaths, recover_case = summary(col, 'All')
    vn_total_case, vn_new_case, vn_deaths_case, vn_new_deaths, vn_recover_case = summary(col, 'Vietnam')
    cn_total_case, cn_new_case, cn_deaths_case, cn_new_deaths, cn_recover_case = summary(col, 'China')
    sk_total_case, sk_new_case, sk_deaths_case, sk_new_deaths, sk_recover_case = summary(col, 'S. Korea')
    # Return the final data.
    if category == 'deaths':
        latest, vn_latest, cn_latest, sk_latest = deaths_case, vn_deaths_case, cn_deaths_case, sk_deaths_case
    elif category == 'recovered':
        latest, vn_latest, cn_latest, sk_latest = recover_case, vn_recover_case, cn_recover_case, sk_recover_case
    else:
        latest, vn_latest, cn_latest, sk_latest = total_case, vn_total_case, cn_total_case, sk_total_case

    return {
        'latest': latest,
        'vn_latest': vn_latest,
        'cn_latest': cn_latest,
        'sk_latest': sk_latest,
        'global_latest': latest - vn_latest,
        'last_updated': last_updated
    }


def statistic_all():
    """
    Return all data statistic and generate message to reply
    """
    data = "\n\n".join([statistic(category) for category in ['deaths', 'recovered', 'confirmed']])
    return data


def statistic(category):
    """
    Return all data statistic and generate message to reply
    """
    category_map = {'deaths': 'tử vong', 'recovered': 'đã được chữa khỏi', 'confirmed': 'bị lây nhiễm'}
    data = get_data(category)
    return "Hiện tại đã có {} người {}.\n" \
           "Tại Việt Nam có {} người\n" \
           "Tại Trung Quốc có {} người\n" \
           "Tại Hàn Quốc có {} người\n" \
           "Trên toàn cầu có {} người\n" \
           "Cập nhật mới nhất vào {}".format(
        data['latest'],
        category_map[category],
        data['vn_latest'],
        data['cn_latest'],
        data['sk_latest'],
        data['global_latest'],
        data['last_updated'])


def handle_data(intent):
    intent_map = {
        'ask_death': 'deaths',
        'ask_resolve': 'recovered',
        'ask_confirm': 'confirmed',
        'ask_all': 'all',
        'fallback': 'fallback'
    }
    if intent_map[intent] in ["deaths", "recovered", "confirmed"]:
        return statistic(intent_map[intent])
    if intent_map[intent] == 'all':
        return statistic_all()
    # When fallback
    return "Chatbot chưa xử lý được nội dung bạn nói. \n\\n Hiện tại chỉ những thông tin sau có thể support. \n1. Thống kê chung tình hình dịch bệnh (VD: Tình hình dịch bệnh hiện nay thế nào) \n2. Hỏi về thống kê số người chết (VD: Có bao nhiêu người chết rồi em)\n3. Hỏi về thống kê số người lây nhiễm (VD: Có bao nhiêu người đã bị lây nhiễm rồi)\n4. Hỏi về thống kê số người được chữa khỏi (VD: Có bao nhiêu người được chữa khỏi rồi)"
