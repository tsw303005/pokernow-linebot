from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from src.pokernow import Pokernow
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def status():
    return "status: ok"

@app.route('/getScore', methods=['POST'])
def getScore():
    url = request.get_json()['url']
    print(url)
    result = pokernow.getScore(url)
    
    return result


if __name__ == '__main__':
    load_dotenv()
    pokernow = Pokernow()
    line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
    handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRETE'))

    app.run(debug=True)
