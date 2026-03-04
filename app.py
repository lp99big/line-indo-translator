import os
import time
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


def translate_text(text):
    """翻譯並自動重試"""
    for i in range(3):
        try:

            # 判斷中文
            if any('\u4e00' <= c <= '\u9fff' for c in text):
                return GoogleTranslator(source='zh-CN', target='id').translate(text)

            # 判斷印尼文
            elif any(word in text.lower() for word in ["apa", "saya", "kamu", "tidak", "ya"]):
                return GoogleTranslator(source='id', target='zh-CN').translate(text)

            # 其他語言 → 中文
            else:
                return GoogleTranslator(source='auto', target='zh-CN').translate(text)

        except Exception as e:
            print("Retry translation:", e)
            time.sleep(1)

    return "⚠️ 翻譯服務暫時無法使用"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_text = event.message.text

    translated = translate_text(user_text)

# 判斷翻譯方向
if any('\u4e00' <= c <= '\u9fff' for c in user_text):
    message = f"〔🇹🇼→ 🇮🇩〕\n{translated}"
else:
    message = f"〔🇮🇩→ 🇹🇼〕\n{translated}"

line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=message)
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
