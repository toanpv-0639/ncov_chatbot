import csv

import requests
from cachetools import cached, TTLCache

from webhook.helpers import date_helpers as date_util

"""
Base URL for fetching data.
"""
base_url = 'https://raw.githubusercontent.com/CSSEGISandData/2019-nCoV/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-%s.csv';


@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def get_data(category):
    """
    Retrieves the data for the provided type.
    """

    # Adhere to category naming standard.
    category = category.lower().capitalize();

    # Request the data
    request = requests.get(base_url % category)
    text = request.text

    # Parse the CSV.
    data = list(csv.DictReader(text.splitlines()))

    # The normalized locations.
    locations = []

    for item in data:
        # Filter out all the dates.
        history = dict(filter(lambda element: date_util.is_date(element[0]), item.items()))

        # Normalize the item and append to locations.
        locations.append({
            # General info.
            'country': item['Country/Region'],
            'province': item['Province/State'],

            # Coordinates.
            'coordinates': {
                'lat': item['Lat'],
                'long': item['Long'],
            },

            # History.
            'history': history,

            # Latest statistic.
            'latest': int(list(history.values())[-1]),

            # Latest datetime.
            'latest_date': date_util.to_date(list(history.keys())[-1]).strftime("%d/%m/%Y"),
        })

    # Latest total.
    latest = sum(map(lambda location: location['latest'], locations))
    vn_latest = sum([location['latest'] for location in locations if location['country'] == 'Vietnam'])
    # Return the final data.
    return {
        'locations': locations,
        'latest': latest,
        'vn_latest': vn_latest,
        'global_latest': latest - vn_latest,
        'latest_date': locations[0]['latest_date']
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
           "Trên toàn cầu có {} người\n" \
           "Cập nhật mới nhất vào {}".format(
        data['latest'],
        category_map[category],
        data['vn_latest'],
        data['global_latest'],
        data['latest_date'])


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
    return "Chatbot chưa xử lý được nội dung bạn nói"
