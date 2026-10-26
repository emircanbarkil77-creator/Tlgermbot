import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot aktif ve güvenli bir şekilde çalışıyor! İçerik satışı için hazır.")

@bot.message_handler(commands=['sat'])
def send_locked_content(message):
    try:
        args = message.text.split()
        stars_price = int(args[1]) if len(args) > 1 else 1
        
        markup = InlineKeyboardMarkup()
        pay_button = InlineKeyboardButton(f"⭐ {stars_price} Yıldız ile Kilidi Aç", pay=True)
        markup.add(pay_button)
        
        bot.send_invoice(
            chat_id=message.chat.id,
            title="Özel İçerik",
            description="Bu içeriği açmak için Telegram Yıldızı ödeyin.",
            invoice_payload="content_unlock_payload",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("İçerik Bedeli", stars_price)],
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"Hata oluştu: {str(e)}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payment = message.successful_payment
    if payment.currency == "XTR":
        bot.send_message(
            message.chat.id, 
            "✅ Ödeme başarılı! İşte gizli içeriğin:\n(Buraya özel fotoğrafı veya medyayı ekleyebilirsin)"
        )

bot.infinity_polling()
