from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from src.command import Command
import os

app = Flask(__name__)
load_dotenv()
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRETE'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    resp = command.makeCommand(event.message.text, line_bot_api,  event)

    if resp != 'return':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=resp))


@app.route('/', methods=['GET'])
def status():
    return "status: ok"


if __name__ == '__main__':
    command = Command()

    app.run(host="0.0.0.0", port="3000", debug=True)
