import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

# Loglama ayarları
logging.basicConfig(level=logging.INFO)

# Token ve Kanal Bilgileri
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@sevgi4500"  # <-- Senin kanalın

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Durum Yönetimi (FSM)
class PostCreation(StatesGroup):
    waiting_for_media = State()
    waiting_for_price = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Bot aktif ve güvenli bir şekilde çalışıyor! 🚀\n\n"
        "Kanala kilitli içerik göndermek için bana bir **fotoğraf veya video** gönder."
    )

# 1. Aşama: Medya geldiğinde bilgileri yakala ve fiyat sor
@dp.message(F.photo | F.video)
async def handle_media(message: types.Message, state: FSMContext):
    media_type = "video" if message.video else "photo"
    file_id = message.video.file_id if message.video else message.photo[-1].file_id
    
    # Süre bilgisi (eğer videoysa)
    duration = message.video.duration if message.video else 0

    # Bilgileri hafızaya al
    await state.update_data(
        file_id=file_id, 
        media_type=media_type, 
        duration=duration,
        caption=message.caption or "Özel İçerik"
    )
    
    await state.set_state(PostCreation.waiting_for_price)
    
    if media_type == "video":
        await message.answer(f"📹 **Video algılandı** (Süre: {duration} saniye).\n\nBu içerik için kaç **Telegram Yıldızı (XTR)** istiyorsun? (Örn: 5)")
    else:
        await message.answer(f"📷 **Fotoğraf algılandı**.\n\nBu içerik için kaç **Telegram Yıldızı (XTR)** istiyorsun? (Örn: 5)")

# 2. Aşama: Fiyat girildiğinde kanala kilitli içeriği gönder
@dp.message(PostCreation.waiting_for_price, F.text.func(lambda text: text.isdigit()))
async def handle_price(message: types.Message, state: FSMContext):
    price = int(message.text)
    data = await state.get_data()
    
    file_id = data["file_id"]
    media_type = data["media_type"]
    duration = data["duration"]
    user_caption = data["caption"]

    # Açıklama metni (medya türü ve süresiyle birlikte)
    if media_type == "video":
        desc = f"🎬 **Özel Video İçeriği**\n⏳ Süre: {duration} saniye\n\n{user_caption}"
    else:
        desc = f"📸 **Özel Fotoğraf İçeriği**\n\n{user_caption}"

    # Fiyat etiketi (XTR)
    prices = [LabeledPrice(label="İçerik Kilidi", amount=price)]

    # Ödeme butonu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⭐ {price} Yıldız ile Kilidi Aç", pay=True)]
    ])

    try:
        # Kanala kilitli medya faturası gönderme
        if media_type == "video":
            await bot.send_invoice(
                chat_id=CHANNEL_ID,
                title="Özel Video",
                description=desc,
                payload=f"content_{file_id[:10]}",
                currency="XTR",
                prices=prices,
                reply_markup=keyboard
            )
        else:
            await bot.send_invoice(
                chat_id=CHANNEL_ID,
                title="Özel Fotoğraf",
                description=desc,
                payload=f"content_{file_id[:10]}",
                currency="XTR",
                prices=prices,
                reply_markup=keyboard
            )
            
        await message.answer(f"✅ Harika! İçerik {price} Yıldız fiyatıyla kanala kilitli olarak gönderildi.")
    except Exception as e:
        await message.answer(f"❌ Bir hata oluştu: {str(e)}\n\n(Lütfen botun @sevgi4500 kanalında **Yönetici** olduğundan emin ol!)")
    
    await state.clear()

@dp.message(PostCreation.waiting_for_price)
async def invalid_price(message: types.Message):
    await message.answer("Lütfen geçerli bir sayı gir!\nÖrnek: `5` veya `10`")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
