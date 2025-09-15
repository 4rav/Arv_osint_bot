import os, re, json, io, time, logging, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from osint_client import lookup_number

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELE_TOKEN:
    logger.error("TELEGRAM_TOKEN not set in env")
    raise SystemExit("TELEGRAM_TOKEN missing")

COOLDOWN = int(os.getenv("COOLDOWN_SECONDS", "3"))
_last_req = {}
PHONE_RE = re.compile(r"^\+?\d{6,15}$")
MAX_MESSAGE_CHARS = 3900

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi — send /lookup <phone-number> (international digits).")

def _format(result):
    if isinstance(result, dict) and "raw" in result and len(result)==1:
        return result["raw"]
    try:
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception:
        return str(result)

async def lookup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    now = time.time()
    last = _last_req.get(uid, 0)
    if now - last < COOLDOWN:
        await update.message.reply_text(f"Please wait a few seconds between requests.")
        return
    _last_req[uid] = now

    if not context.args:
        await update.message.reply_text("Usage: /lookup <phone-number>")
        return
    number = context.args[0].strip()
    if not re.match(r"^\+?\d{6,15}$", number):
        await update.message.reply_text("Invalid number format. Use only digits, optional leading +.")
        return

    await update.message.reply_text("Looking up...")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, lookup_number, number)

    if isinstance(result, dict) and result.get("error"):
        await update.message.reply_text(f"API error: {result}")
        logger.warning("API error for %s -> %s", number, result)
        return

    text = _format(result)
    if len(text) <= MAX_MESSAGE_CHARS:
        await update.message.reply_text(text)
    else:
        bio = io.BytesIO(text.encode("utf-8"))
        bio.name = f"{number}_result.json"
        await update.message.reply_document(document=bio)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/lookup <number>")

def main():
    app = ApplicationBuilder().token(TELE_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lookup", lookup_handler))
    app.add_handler(CommandHandler("help", help_cmd))
    logger.info("Starting bot (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
