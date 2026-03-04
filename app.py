import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from googletrans import Translator

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

translator = Translator()

@app.route("/")
def home():
    return "LINE Indo Translator Bot Running"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(e)
        return "Error", 500

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    try:
        if any('\u4e00' <= char <= '\u9fff' for char in user_text):
            result = translator.translate(user_text, src='zh-cn', dest='id')
        else:
            result = translator.translate(user_text, src='id', dest='zh-cn')

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result.text)
        )

    except Exception as e:
        print(e)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="翻譯失敗，請稍後再試")
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
