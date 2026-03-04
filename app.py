import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from deep_translator import GoogleTranslator

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/")
def home():
    return "LINE Indo Translator Bot Running"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("Webhook Error:", e)
        return "Error", 500

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    try:
        # 判斷是否含中文
        if any('\u4e00' <= char <= '\u9fff' for char in user_text):
            # 中文 -> 印尼
            translated = GoogleTranslator(source='zh-CN', target='id').translate(user_text)
        else:
            # 印尼 -> 中文
            translated = GoogleTranslator(source='id', target='zh-CN').translate(user_text)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=translated)
        )

    except Exception as e:
        print("Translation Error:", e)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ 翻譯暫時失敗，請稍後再試")
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
