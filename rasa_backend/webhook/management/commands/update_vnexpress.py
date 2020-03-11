from django.core.management.base import BaseCommand

from backend.settings import ROOMID_NOTICE
from webhook.helpers.vnexpress_helpers import *
from webhook.helpers.chatwork_helpers import *

class Command(BaseCommand):
    help = 'Update VnExpress'

    def handle(self, *args, **options):
        chatwork = Chatwork()
        href, title = get_newest_health()
        if check_news(href, title):
            content = "Link chi tiết: {}".format(href)
            chatwork.send_message(room_id=ROOMID_NOTICE,
                                  message=chatwork.notice_message(title, content))
        self.stdout.write(self.style.SUCCESS('Update VnExpress successfully'))
