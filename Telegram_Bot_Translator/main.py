import os
import sys
import asyncio
import logging
from collections import defaultdict

from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_TARGET_LANG = os.getenv("DEFAULT_TARGET_LANG", "en")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Put it into .env")

user_target_lang = defaultdict(lambda: DEFAULT_TARGET_LANG)
user_menu_on = defaultdict(lambda: False)

LANG_CHOICES = [
    ("English", "en"),
    ("Русский", "ru"),
    ("Қазақша", "kk"),
    ("Türkçe", "tr"),
    ("Deutsch", "de"),
    ("Español", "es"),
    ("Français", "fr"),
    ("中文", "zh-cn"),
]


def make_inline_lang_keyboard() -> InlineKeyboardMarkup:
    rows, row = [], []
    for i, (title, code) in enumerate(LANG_CHOICES, start=1):
        row.append(InlineKeyboardButton(title, callback_data=f"setlang:{code}"))
        if i % 3 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def make_reply_menu(selected: str) -> ReplyKeyboardMarkup:
    row1 = ["en", "ru", "kk"]
    row2 = ["tr", "de", "es"]
    row3 = ["fr", "zh-cn", f"current:{selected}"]
    return ReplyKeyboardMarkup([row1, row2, row3], resize_keyboard=True)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда. Попробуйте /help")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    tgt = user_target_lang[uid]
    text = (
        "👋 Привет! Я бот-переводчик.\n\n"
        "Отправь мне текст — переведу его.\n"
        f"Текущий язык перевода: {tgt}\n\n"
        "Поменять язык: /setlang <код> или кнопки ниже.\n"
        "Список кодов: /langs\n"
        "Включить большие кнопки: /menu  ·  Выключить: /menu_off\n"
    )
    # Без MarkdownV2 — безопасно и стабильно
    await update.message.reply_text(text, reply_markup=make_inline_lang_keyboard())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Команды:\n"
        "/start — приветствие и выбор языка\n"
        "/help — эта справка\n"
        "/setlang <код> — установить язык перевода (например: /setlang en)\n"
        "/langs — популярные коды языков\n"
        "/menu — показать большие кнопки с языками\n"
        "/menu_off — убрать большие кнопки\n"
        "Просто пришлите текст — я переведу его, автоматически определив исходный язык."
    )


async def langs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    codes = ", ".join(sorted({code for _, code in LANG_CHOICES}))
    await update.message.reply_text(
        f"Популярные коды языков: {codes}\n\n"
        "Выберите кнопкой ниже или используйте /setlang <код>.",
        reply_markup=make_inline_lang_keyboard(),
    )


async def setlang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        await update.message.reply_text(
            "Укажите код языка, например: /setlang en",
            reply_markup=make_inline_lang_keyboard(),
        )
        return
    code = context.args[0].lower()
    user_target_lang[uid] = code

    reply = make_reply_menu(code) if user_menu_on[uid] else None
    await update.message.reply_text(
        f"✅ Язык перевода установлен: {code}",
        reply_markup=reply or make_inline_lang_keyboard(),
    )


async def menu_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_menu_on[uid] = True
    tgt = user_target_lang[uid]
    await update.message.reply_text(
        "📌 Большие кнопки включены.",
        reply_markup=make_reply_menu(tgt),
    )


async def menu_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_menu_on[uid] = False
    await update.message.reply_text(
        "🗑️ Большие кнопки скрыты.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data:
        return

    if query.data.startswith("setlang:"):
        code = query.data.split(":", 1)[1]
        uid = query.from_user.id
        user_target_lang[uid] = code

        await query.edit_message_text(
            text=f"✅ Язык перевода установлен: {code}\nОтправьте сообщение для перевода.",
            reply_markup=make_inline_lang_keyboard(),
        )


async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    target = user_target_lang[uid]
    src_text = update.message.text or ""

    normalized = src_text.strip().lower()
    if normalized in {c for _, c in LANG_CHOICES}:
        user_target_lang[uid] = normalized
        reply = make_reply_menu(normalized) if user_menu_on[uid] else None
        await update.message.reply_text(
            f"✅ Язык перевода установлен: {normalized}",
            reply_markup=reply or make_inline_lang_keyboard(),
        )
        return
    if normalized.startswith("current:"):
        pass

    if not src_text:
        return

    try:
        translator = GoogleTranslator(source="auto", target=target)
        translated = translator.translate(src_text)

        reply_markup = make_inline_lang_keyboard()
        if user_menu_on[uid]:
            pass

        await update.message.reply_text(
            f"🗣️ ➡️ ({target})\n{translated}",
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.exception("Translation failed: %s", e)
        await update.message.reply_text(
            "❌ Не удалось перевести. Попробуйте позже или смените язык /setlang.",
            reply_markup=make_inline_lang_keyboard(),
        )


async def post_init(app: Application):
    logger.info("Bot launched.")


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("setlang", setlang_cmd))
    application.add_handler(CommandHandler("langs", langs_cmd))
    application.add_handler(CommandHandler("menu", menu_on))
    application.add_handler(CommandHandler("menu_off", menu_off))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    application.add_handler(CallbackQueryHandler(on_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()