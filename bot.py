import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import os

# --- Telegram Bot Token ---
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set this in Render Environment Variables

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- Command /start ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("👋 Hello! Send me a mobile number to get OSINT report.")

# --- Handler for mobile numbers ---
@dp.message_handler()
async def fetch_info(message: types.Message):
    mobile = message.text.strip()
    url = f"https://swapi-num-api.onrender.com/info?api_key=swapipy&mobile={mobile}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception as e:
        await message.reply(f"❌ Error fetching data: {e}")
        return

    result = data.get("data", [])
    if not result:
        await message.reply("❌ No matching records found in the OSINT database.")
        return

    msg = "📑 *OSINT Intelligence Report*\n"
    msg += "━━━━━━━━━━━━━━━━━━━\n\n"

    for entry in result:
        msg += f"👤 *Name:* `{entry.get('name','N/A')}`\n"
        msg += f"👨‍👦 *Father’s Name:* `{entry.get('fname','N/A')}`\n"
        msg += f"📱 *Primary Mobile:* `{entry.get('mobile','N/A')}`\n"
        msg += f"☎️ *Alternate Mobile:* `{entry.get('alt','N/A')}`\n"
        msg += f"🏠 *Residential Address:* `{entry.get('address','N/A')}`\n"
        msg += f"🌍 *Circle / Region:* `{entry.get('circle','N/A')}`\n"
        msg += "━━━━━━━━━━━━━━━━━━━\n\n"

    msg += "✅ *Report Generated Successfully*\n"
    msg += "_Confidential OSINT Data — For Investigative Use Only_"

    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
