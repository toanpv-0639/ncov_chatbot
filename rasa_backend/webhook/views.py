import json

import random
import re
import requests
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from backend.settings import SECRET_KEY, FB_TOKEN
from webhook.helpers.chatbot_helpers import RasaHelpers
from webhook.helpers.chatwork_helpers import Chatwork


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


FB_ENDPOINT = 'https://graph.facebook.com/v2.12/'
PAGE_ACCESS_TOKEN = FB_TOKEN

# bot.logic.py
LOGIC_RESPONSES = {
    'account': [
        "You can find your account information on https://www.codingforentrepreneurs.com/account/"
    ],
    'enroll': [
        "You can simply enroll on https://www.codingforentrepreneurs.com/enroll/"
    ],
    "projects": [
        "All of our projects are on http://joincfe.com/projects and courses are on http://joincfe.com/courses/"
    ],
    "free": [
        "All of our free content is on http://joincfe.com/youtube/."
    ],
    "membership": [
        "You can enroll for a pro membership on http://joincfe.com/enroll/ to get access to all of our content in HD!"
    ],
    "afford": [
        "Have you thought about subscribing to our free YouTube channel?  It's on http://joincfe.com/youtube/."
    ],
    "blog": [
        "Our blog is on http://joincfe.com/blog/"
    ],
    "guides": [
        "You can access our guides blog is on http://joincfe.com/blog/"
    ],
    "thank": [
        "Of course!",
        "Anytime!",
        "You're welcome",
        "You are so welcome!"
    ],
    "thanks": [
        "Of course!",
        "Anytime!",
        "You're welcome",
        "You are so welcome!"
    ],
    'help': [
        "A good place to get help is by going to our forums on http://joincfe.com/ask/",
        "You can always ask questions in our videos or on http://joincfe.com/ask/"
    ],
    'code': [
        "Have you considered looking at our code on http://joincfe.com/github/? That might help you",
        "We don't review code at this time, but you can consider looking at our open-source repo http://joincfe.com/github/"
    ],
    'human': [
        'A real person will get back to you shortly!'
    ]
}


def parse_and_send_fb_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    msg = get_bot_response(recevied_message)

    if msg is not None:
        endpoint = f"{FB_ENDPOINT}/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": msg}})
        status = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            data=response_msg)
        return status.json()
    return None


class FacebookWebhookView(View):
    @method_decorator(csrf_exempt)  # required
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)  # python3.6+ syntax

    '''
    hub.mode
    hub.verify_token
    hub.challenge
    Are all from facebook. We'll discuss soon.
    '''

    def get(self, request, *args, **kwargs):
        hub_mode = request.GET.get('hub.mode')
        hub_token = request.GET.get('hub.verify_token')
        hub_challenge = request.GET.get('hub.challenge')
        if hub_token != SECRET_KEY:
            return HttpResponse('Error, invalid token', status=403)
        return HttpResponse(hub_challenge)

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    fb_user_id = message['sender']['id']  # sweet!
                    fb_user_txt = message['message'].get('text')
                    if fb_user_txt:
                        parse_and_send_fb_message(fb_user_id, fb_user_txt)
        return HttpResponse("Success", status=200)
