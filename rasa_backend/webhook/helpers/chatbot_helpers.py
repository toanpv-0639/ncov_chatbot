import requests
import json
from backend.settings import RASA_DOMAIN, RASA_NLU_POST_URL, RASA_MIN_CONFIDENCE
from webhook.helpers.data_helpers import handle_data

class RasaHelpers():
    def __init__(self):
        self.headers = {
            'Content-Type': "application/json",
            'Host': RASA_DOMAIN,
        }
        self.url = RASA_NLU_POST_URL

    def detect_intent(self, response):
        if response['intent']:
            print(response['intent']['confidence'])
            if response['intent']['confidence'] > RASA_MIN_CONFIDENCE:
                return response['intent']['name']
        return "fallback"

    def post_nlu(self, message):
        payload = {
            "text": message
        }
        response = requests.request("POST", self.url, data=json.dumps(payload), headers=self.headers)
        return json.loads(response.text)

    def handle_message(self, message, top_k):
        response = self.post_nlu(message)
        intent = self.detect_intent(response)
        return handle_data(intent, top_k)
