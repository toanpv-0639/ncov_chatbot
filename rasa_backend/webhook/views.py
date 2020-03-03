import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from webhook.helpers.chatbot_helpers import RasaHelpers
from webhook.helpers.chatwork_helpers import Chatwork
from backend.settings import SECRET_KEY

def decode_payload(request):
    payload = str(request.body, encoding='utf-8')
    return json.loads(payload)

def get_bot_response(message):
    rasa = RasaHelpers()
    bot_response = rasa.handle_message(message)
    return bot_response

def handle_chatwork_payload(payload):
    if payload['webhook_event_type'] == 'mention_to_me' and '[toall]' not in payload['webhook_event']['body']:
        chatwork = Chatwork()
        message_body = payload['webhook_event']['body'].split('\n')[-1]
        message_reply_chatwork = chatwork.reply_message(
            account_id=int(payload['webhook_event']['from_account_id']),
            room_id=int(payload['webhook_event']['room_id']),
            message_id=int(payload['webhook_event']['message_id']),
            message=get_bot_response(message_body)
        )
        chatwork.send_message(room_id=payload['webhook_event']['room_id'], message=message_reply_chatwork)


# Create your views here.
@csrf_exempt
def chatwork_webhook(request):
    payload = decode_payload(request)
    handle_chatwork_payload(payload)
    return HttpResponse('Webhook received', status=200)

# Create your views here.
@csrf_exempt
def facebook_webhook(request):
    if request.GET.get('hub.verify_token') == SECRET_KEY:
        return HttpResponse(request.GET.get('hub.challenge'))
    else:
        return HttpResponse('Invalid Token !')

