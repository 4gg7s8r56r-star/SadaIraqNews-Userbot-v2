import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

API_ID = 35521304
API_HASH = '40c6426dfd0d378895510f00727e2f86'
SESSION_STRING = os.getenv('SESSION_STRING')
TARGET_CHANNEL = 'SadaIraqNews1'  # يوزر قناتك

# القنوات المصدر وإعداداتها
# media: True تعني نقل كل شيء (نصوص، صور، فيديو)
# media: False تعني نقل النصوص فقط وتجاهل الوسائط
SOURCES = {
    'AjaNews': {'media': False},
    'SabrenNewss': {'media': False},
    'Iraq_now3': {'media': True},
    'ONEIQ1': {'media': True}
}

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# لتجنب التكرار (تخزين آخر 50 رسالة)
processed_messages = []

def clean_text(text):
    if not text:
        return ""
    # إزالة الروابط
    text = re.sub(r'http\S+', '', text)
    # إضافة رابط قناتك
    text += f"\n\n🔗 تابعونا على: https://t.me/{TARGET_CHANNEL}"
    return text

@client.on(events.NewMessage(chats=list(SOURCES.keys())))
async def handler(event):
    chat = await event.get_chat()
    username = chat.username
    
    if not username or username not in SOURCES:
        return

    # التحقق من التكرار (بناءً على النص)
    msg_text = event.message.message
    if msg_text and msg_text in processed_messages:
        return
    
    if msg_text:
        processed_messages.append(msg_text)
        if len(processed_messages) > 50:
            processed_messages.pop(0)

    cleaned_text = clean_text(msg_text)
    
    # التعامل مع الوسائط
    allow_media = SOURCES[username]['media']
    
    try:
        if event.message.media:
            if allow_media:
                # إرسال مع الوسائط (صور/فيديو) للقنوات المسموح لها
                await client.send_file(TARGET_CHANNEL, event.message.media, caption=cleaned_text)
            else:
                # إذا كانت الميديا غير مسموحة (مثل الجزيرة)، نرسل النص فقط إذا وجد
                if cleaned_text.strip():
                    await client.send_message(TARGET_CHANNEL, cleaned_text)
        else:
            # رسالة نصية فقط
            if cleaned_text.strip():
                await client.send_message(TARGET_CHANNEL, cleaned_text)
    except Exception as e:
        print(f"Error forwarding message: {e}")

async def main():
    await client.start()
    print("Userbot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
