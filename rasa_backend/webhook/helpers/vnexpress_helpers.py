import requests
from bs4 import BeautifulSoup
from webhook.models import Page

def get_newest_health():
    try:
        url = 'https://vnexpress.net/suc-khoe'
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        article_tag = soup.findAll("div", {"class": "thumb_big"})[0]
        a_tag = article_tag.find('a', {'class': 'thumb'})

        return a_tag.get('href'), a_tag.get('title')
    except:
        return None, None


def check_title(title):
    # Check title is valid
    if "âm tính" in title or "dương tính" in title or "nghi nhiễm" in title or "ca nhiễm" in title:
        return True
    return False

def check_news(href, title):
    # Check news exist in database. When exist not send message
    page = Page.objects.filter(href=href).first()
    if page:
        return False
    # Check title when not exist in database
    if check_title(title):
        Page(href=href, title=title).save()
        return True
    return False


