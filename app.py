from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from src.command import Command
import os
import json

app = Flask(__name__)
load_dotenv()
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRETE'))
command = Command()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        message = f'\nuser: {profile.display_name}\nuser_id: {event.source.user_id}\ncommand: {event.message.text}\n'
        app.logger.info(message)
        resp = command.makeCommand(event.message.text, event.source.user_id, event.source.group_id)
        if resp != '':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=str(resp)))
    except Exception as err:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(err)))


@app.route('/', methods=['GET'])
def status():
    return "status: ok"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="3000", debug=True)
