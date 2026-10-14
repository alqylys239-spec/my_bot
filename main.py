import os
import threading
import telebot
from flask import Flask

# جلب توكن البوت من متغيرات البيئة في Render للأمان
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@shbin4"  # معرّف قناتك

bot = telebot.TeleBot(TOKEN)

# 1. إنشاء سيرفر Web لمنع وضع السكون (Sleep Mode) على Render مدى الحياة
app = Flask("")


@app.route("/")
def home():
  return "البوت يعمل بنجاح 24/7 مع الاشتراك الإجباري! 🚀"


def run_flask():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


# دالة للتحقق مما إذا كان المستخدم مشتركاً في القناة أم لا
def is_user_subscribed(user_id):
  try:
    member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    # الحالات التي تؤكد أن المستخدم عضو أو مشرف أو مالك القناة
    if member.status in ["creator", "administrator", "member"]:
      return True
    return False
  except Exception as e:
    print(f"خطأ في فحص الاشتراك (تأكد أن البوت أدمن بالقناة): {e}")
    # في حال حدوث مشكلة تقنية، يسمح بالمرور مؤقتاً لئلا يتوقف البوت
    return True


# 2. أمر /start مع التحقق من الاشتراك الإجباري
@bot.message_handler(commands=["start"])
def send_welcome(message):
  user_id = message.from_user.id
  first_name = message.from_user.first_name

  if not is_user_subscribed(user_id):
    bot.reply_to(
        message,
        f"عذراً يا {first_name}! ⚠️\n\n"
        f"يجب عليك الاشتراك في قناتنا أولاً لتتمكن من استخدام البوت:\n"
        f"👉 {CHANNEL_USERNAME}\n\n"
        f"بعد الاشتراك، أرسل /start مرة أخرى.",
    )
  else:
    bot.reply_to(
        message,
        "أهلاً بك! أنت مشترك في القناة والبوت يعمل معك بنجاح 🚀",
    )


# 3. الاشتراك الإجباري الدائم على مستوى المجموعة (مع كل رسالة)
@bot.message_handler(func=lambda message: True)
def enforce_channel_subscription(message):
  # نتحقق إذا كانت الرسالة داخل مجموعة وليست في الخاص
  if message.chat.type in ["group", "supergroup"]:
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # استثناء المشرفين من شرط الاشتراك الإجباري
    try:
      chat_member = bot.get_chat_member(message.chat.id, user_id)
      if chat_member.status in ["creator", "administrator"]:
        return  # إذا كان مشرفاً في المجموعة، لا نطب عليه الاشتراك
    except:
      pass

    # فحص الاشتراك في القناة
    if not is_user_subscribed(user_id):
      try:
        # حذف رسالة غير المشترك لضمان الالتزام
        bot.delete_message(message.chat.id, message.message_id)
      except:
        pass

      # إرسال تنبيه مؤقت له
      warning_msg = bot.send_message(
          message.chat.id,
          f"عذراً يا {first_name} 🚫\n"
          f"يجب عليك الاشتراك في قناة البوت لتتمكن من التفاعل هنا:\n"
          f"👉 {CHANNEL_USERNAME}",
      )
      # يمكنك ترك الرسالة أو جعل البوت يحذفها بعد فترة إذا أردت


if __name__ == "__main__":
  # تشغيل سيرفر Flask في خيط منفصل لمنع السكون 24/7
  t = threading.Thread(target=run_flask)
  t.start()

  print("البوت يعمل الآن مدى الحياة...")
  bot.infinity_polling()
