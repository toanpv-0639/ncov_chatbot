from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from webhook.helpers.chatbot_helpers import RasaHelpers
from webhook.helpers.chatwork_helpers import Chatwork


def decode_payload(request):
    payload = str(request.body, encoding='utf-8')
    return json.loads(payload)


def handle_payload(payload):
    if payload['webhook_event_type'] == 'mention_to_me':
        rasa = RasaHelpers()
        chatwork = Chatwork()
        message_body = payload['webhook_event']['body'].split('\n')[-1]
        bot_response = rasa.handle_message(message_body)

        message_reply_chatwork = chatwork.reply_message(
            account_id=int(payload['webhook_event']['from_account_id']),
            room_id=int(payload['webhook_event']['room_id']),
            message_id=int(payload['webhook_event']['message_id']),
            message=bot_response
        )
        chatwork.send_message(room_id=payload['webhook_event']['room_id'], message=message_reply_chatwork)


# Create your views here.
@csrf_exempt
def chatwork_webhook(request):
    payload = decode_payload(request)
    handle_payload(payload)
    return HttpResponse('Webhook received', status=200)
