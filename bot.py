"""
GarageLog Feedback Bot — multilingual, без ConversationHandler
"""

import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ─── Переводы ─────────────────────────────────────────────────────────────────

STRINGS = {
    "ru": {
        "welcome":         "👋 Привет! Это бот обратной связи *GarageLog*.\n\nВыбери, что хочешь сделать:",
        "btn_bug":         "🐛 Сообщить об ошибке",
        "btn_idea":        "💡 Предложить идею",
        "btn_feedback":    "💬 Общий отзыв",
        "btn_language":    "🌐 Язык / Language",
        "choose_lang":     "🌐 Выбери язык:",
        "lang_set":        "✅ Язык: Русский\n\n",
        "prompt_bug":      "🐛 Опиши ошибку:\n• что делал\n• что ожидал\n• что произошло\n• устройство / браузер\n\nИли /cancel для отмены.",
        "prompt_idea":     "💡 Расскажи идею — что добавить или изменить?\n\nИли /cancel для отмены.",
        "prompt_feedback": "💬 Напиши отзыв — что нравится, что нет?\n\nИли /cancel для отмены.",
        "thanks_bug":      "✅ Спасибо! Разберёмся с ошибкой.",
        "thanks_idea":     "✅ Отличная идея! Возьмём в работу.",
        "thanks_feedback": "✅ Спасибо за отзыв!",
        "more":            "\n\nХочешь написать ещё?",
        "cancelled":       "Отменено. Напиши /start чтобы начать снова.",
        "label_bug":       "🐛 Ошибка",
        "label_idea":      "💡 Идея",
        "label_feedback":  "💬 Отзыв",
        "reply_from":      "📨 *Ответ от разработчика GarageLog:*\n\n",
    },
    "en": {
        "welcome":         "👋 Hi! This is the *GarageLog* feedback bot.\n\nWhat would you like to do?",
        "btn_bug":         "🐛 Report a bug",
        "btn_idea":        "💡 Suggest an idea",
        "btn_feedback":    "💬 General feedback",
        "btn_language":    "🌐 Language",
        "choose_lang":     "🌐 Choose your language:",
        "lang_set":        "✅ Language: English\n\n",
        "prompt_bug":      "🐛 Describe the bug:\n• what you did\n• what you expected\n• what happened\n• device / browser\n\nOr /cancel to abort.",
        "prompt_idea":     "💡 Tell us your idea — what to add or change?\n\nOr /cancel to abort.",
        "prompt_feedback": "💬 Share your feedback — what do you like or dislike?\n\nOr /cancel to abort.",
        "thanks_bug":      "✅ Thanks! We'll look into the bug.",
        "thanks_idea":     "✅ Great idea! We'll consider it.",
        "thanks_feedback": "✅ Thanks for the feedback!",
        "more":            "\n\nWant to send something else?",
        "cancelled":       "Cancelled. Write /start to begin again.",
        "label_bug":       "🐛 Bug",
        "label_idea":      "💡 Idea",
        "label_feedback":  "💬 Feedback",
        "reply_from":      "📨 *Reply from the GarageLog developer:*\n\n",
    },
    "zh": {
        "welcome":         "👋 你好！这是 *GarageLog* 反馈机器人。\n\n请选择：",
        "btn_bug":         "🐛 报告错误",
        "btn_idea":        "💡 提出建议",
        "btn_feedback":    "💬 综合反馈",
        "btn_language":    "🌐 语言",
        "choose_lang":     "🌐 选择语言：",
        "lang_set":        "✅ 语言：中文\n\n",
        "prompt_bug":      "🐛 请描述错误：\n• 你做了什么\n• 期望什么\n• 发生了什么\n• 设备 / 浏览器\n\n或 /cancel 取消。",
        "prompt_idea":     "💡 请告诉我们你的想法\n\n或 /cancel 取消。",
        "prompt_feedback": "💬 请分享你的反馈\n\n或 /cancel 取消。",
        "thanks_bug":      "✅ 谢谢！我们会调查。",
        "thanks_idea":     "✅ 好主意！",
        "thanks_feedback": "✅ 感谢反馈！",
        "more":            "\n\n还想发送其他内容吗？",
        "cancelled":       "已取消。输入 /start 重新开始。",
        "label_bug":       "🐛 错误",
        "label_idea":      "💡 建议",
        "label_feedback":  "💬 反馈",
        "reply_from":      "📨 *GarageLog 开发者回复：*\n\n",
    },
    "es": {
        "welcome":         "👋 ¡Hola! Este es el bot de feedback de *GarageLog*.\n\n¿Qué quieres hacer?",
        "btn_bug":         "🐛 Reportar un error",
        "btn_idea":        "💡 Sugerir una idea",
        "btn_feedback":    "💬 Feedback general",
        "btn_language":    "🌐 Idioma",
        "choose_lang":     "🌐 Elige tu idioma:",
        "lang_set":        "✅ Idioma: Español\n\n",
        "prompt_bug":      "🐛 Describe el error:\n• qué hiciste\n• qué esperabas\n• qué pasó\n• dispositivo / navegador\n\nO /cancel para cancelar.",
        "prompt_idea":     "💡 Cuéntanos tu idea\n\nO /cancel para cancelar.",
        "prompt_feedback": "💬 Comparte tu opinión\n\nO /cancel para cancelar.",
        "thanks_bug":      "✅ ¡Gracias! Investigaremos.",
        "thanks_idea":     "✅ ¡Buena idea!",
        "thanks_feedback": "✅ ¡Gracias por el feedback!",
        "more":            "\n\n¿Quieres enviar algo más?",
        "cancelled":       "Cancelado. Escribe /start para empezar.",
        "label_bug":       "🐛 Error",
        "label_idea":      "💡 Idea",
        "label_feedback":  "💬 Feedback",
        "reply_from":      "📨 *Respuesta del desarrollador:*\n\n",
    },
    "de": {
        "welcome":         "👋 Hallo! Dies ist der Feedback-Bot von *GarageLog*.\n\nWas möchtest du tun?",
        "btn_bug":         "🐛 Fehler melden",
        "btn_idea":        "💡 Idee vorschlagen",
        "btn_feedback":    "💬 Allgemeines Feedback",
        "btn_language":    "🌐 Sprache",
        "choose_lang":     "🌐 Wähle deine Sprache:",
        "lang_set":        "✅ Sprache: Deutsch\n\n",
        "prompt_bug":      "🐛 Beschreibe den Fehler:\n• was du gemacht hast\n• was du erwartet hast\n• was passiert ist\n• Gerät / Browser\n\nOder /cancel zum Abbrechen.",
        "prompt_idea":     "💡 Erzähl uns deine Idee\n\nOder /cancel zum Abbrechen.",
        "prompt_feedback": "💬 Teile dein Feedback\n\nOder /cancel zum Abbrechen.",
        "thanks_bug":      "✅ Danke! Wir untersuchen den Fehler.",
        "thanks_idea":     "✅ Tolle Idee!",
        "thanks_feedback": "✅ Danke für dein Feedback!",
        "more":            "\n\nMöchtest du noch etwas senden?",
        "cancelled":       "Abgebrochen. Schreib /start zum Neustart.",
        "label_bug":       "🐛 Fehler",
        "label_idea":      "💡 Idee",
        "label_feedback":  "💬 Feedback",
        "reply_from":      "📨 *Antwort vom Entwickler:*\n\n",
    },
    "fr": {
        "welcome":         "👋 Bonjour ! Ceci est le bot de retour de *GarageLog*.\n\nQue souhaitez-vous faire ?",
        "btn_bug":         "🐛 Signaler un bug",
        "btn_idea":        "💡 Proposer une idée",
        "btn_feedback":    "💬 Retour général",
        "btn_language":    "🌐 Langue",
        "choose_lang":     "🌐 Choisissez votre langue :",
        "lang_set":        "✅ Langue : Français\n\n",
        "prompt_bug":      "🐛 Décrivez le bug :\n• ce que vous avez fait\n• ce que vous attendiez\n• ce qui s'est passé\n• appareil / navigateur\n\nOu /cancel pour annuler.",
        "prompt_idea":     "💡 Partagez votre idée\n\nOu /cancel pour annuler.",
        "prompt_feedback": "💬 Partagez votre avis\n\nOu /cancel pour annuler.",
        "thanks_bug":      "✅ Merci ! Nous allons examiner.",
        "thanks_idea":     "✅ Bonne idée !",
        "thanks_feedback": "✅ Merci pour votre retour !",
        "more":            "\n\nVoulez-vous envoyer autre chose ?",
        "cancelled":       "Annulé. Écrivez /start pour recommencer.",
        "label_bug":       "🐛 Bug",
        "label_idea":      "💡 Idée",
        "label_feedback":  "💬 Retour",
        "reply_from":      "📨 *Réponse du développeur :*\n\n",
    },
}

LANG_MAP = {
    "ru": "ru", "be": "ru", "uk": "ru",
    "en": "en",
    "zh": "zh",
    "es": "es",
    "de": "de",
    "fr": "fr",
}

LANG_BUTTONS = [
    ("🇷🇺 Русский", "lang:ru"),
    ("🇬🇧 English",  "lang:en"),
    ("🇨🇳 中文",      "lang:zh"),
    ("🇪🇸 Español",  "lang:es"),
    ("🇩🇪 Deutsch",  "lang:de"),
    ("🇫🇷 Français", "lang:fr"),
]

# Состояние ожидания текста: храним в user_data["awaiting"]
# Значения: "bug" | "idea" | "feedback" | None

def get_lang(user, ctx) -> str:
    if ctx.user_data.get("lang"):
        return ctx.user_data["lang"]
    code = (user.language_code or "en").lower().split("-")[0]
    return LANG_MAP.get(code, "en")

def s(user, ctx, key) -> str:
    return STRINGS.get(get_lang(user, ctx), STRINGS["en"])[key]

def username_str(user) -> str:
    name = user.full_name
    if user.username:
        name += f" (@{user.username})"
    return name

def now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")

def main_kb(user, ctx):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(s(user, ctx, "btn_bug"),      callback_data="action:bug")],
        [InlineKeyboardButton(s(user, ctx, "btn_idea"),     callback_data="action:idea")],
        [InlineKeyboardButton(s(user, ctx, "btn_feedback"), callback_data="action:feedback")],
        [InlineKeyboardButton(s(user, ctx, "btn_language"), callback_data="show_langs")],
    ])

def lang_kb():
    rows = []
    for i in range(0, len(LANG_BUTTONS), 2):
        rows.append([InlineKeyboardButton(label, callback_data=cb)
                     for label, cb in LANG_BUTTONS[i:i+2]])
    return InlineKeyboardMarkup(rows)


# ─── Хэндлеры ─────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ctx.user_data["awaiting"] = None
    await update.message.reply_text(
        s(user, ctx, "welcome"),
        parse_mode="Markdown",
        reply_markup=main_kb(user, ctx),
    )

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ctx.user_data["awaiting"] = None
    await update.message.reply_text(s(user, ctx, "cancelled"))

async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(s(user, ctx, "choose_lang"), reply_markup=lang_kb())

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = q.from_user
    data = q.data

    await q.answer()

    # Выбор языка — открываем список
    if data == "show_langs":
        await q.edit_message_text(s(user, ctx, "choose_lang"), reply_markup=lang_kb())
        return

    # Установка языка
    if data.startswith("lang:"):
        lang = data.split(":")[1]
        ctx.user_data["lang"] = lang
        await q.edit_message_text(
            STRINGS[lang]["lang_set"] + STRINGS[lang]["welcome"],
            parse_mode="Markdown",
            reply_markup=main_kb(user, ctx),
        )
        return

    # Выбор типа обращения
    if data.startswith("action:"):
        kind = data.split(":")[1]
        ctx.user_data["awaiting"] = kind
        prompt_key = {"bug": "prompt_bug", "idea": "prompt_idea", "feedback": "prompt_feedback"}[kind]
        await q.edit_message_text(s(user, ctx, prompt_key))
        return

    # Ответ админа пользователю
    if data.startswith("reply:"):
        if user.id != ADMIN_ID:
            return
        _, user_id, user_name = data.split(":", 2)
        ctx.user_data["reply_to_id"]   = int(user_id)
        ctx.user_data["reply_to_name"] = user_name
        await q.edit_message_reply_markup(None)
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✏️ Напиши ответ для *{user_name}* (или /cancel):",
            parse_mode="Markdown",
        )

async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # Ответ админа
    if user.id == ADMIN_ID and ctx.user_data.get("reply_to_id"):
        uid   = ctx.user_data.pop("reply_to_id")
        uname = ctx.user_data.pop("reply_to_name", "")
        try:
            await ctx.bot.send_message(
                chat_id=uid,
                text=f"📨 *Reply from GarageLog developer:*\n\n{text}",
                parse_mode="Markdown",
            )
            await update.message.reply_text(f"✅ Отправлено: {uname}")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
        return

    # Ожидаем фидбек от пользователя
    kind = ctx.user_data.get("awaiting")
    if not kind:
        await update.message.reply_text(
            s(user, ctx, "welcome"),
            parse_mode="Markdown",
            reply_markup=main_kb(user, ctx),
        )
        return

    ctx.user_data["awaiting"] = None

    label_key = {"bug": "label_bug", "idea": "label_idea", "feedback": "label_feedback"}
    label = s(user, ctx, label_key[kind])
    lang  = get_lang(user, ctx)

    admin_msg = (
        f"{label} *— новое сообщение*\n"
        f"──────────────────\n"
        f"👤 {username_str(user)}\n"
        f"🆔 `{user.id}`\n"
        f"🌐 `{lang}` (tg: `{user.language_code}`)\n"
        f"🕐 {now()}\n"
        f"──────────────────\n"
        f"{text}"
    )
    reply_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("↩️ Ответить", callback_data=f"reply:{user.id}:{user.full_name}")
    ]])

    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_msg,
            parse_mode="Markdown",
            reply_markup=reply_kb,
        )
    except Exception as e:
        log.error("Forward error: %s", e)

    thanks_key = {"bug": "thanks_bug", "idea": "thanks_idea", "feedback": "thanks_feedback"}
    await update.message.reply_text(
        s(user, ctx, thanks_key[kind]) + s(user, ctx, "more"),
        reply_markup=main_kb(user, ctx),
    )

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not ctx.args:
        await update.message.reply_text("Использование: /broadcast Текст")
        return
    text = " ".join(ctx.args)
    try:
        with open("users.txt") as f:
            uids = [int(l.strip()) for l in f if l.strip()]
    except FileNotFoundError:
        await update.message.reply_text("users.txt не найден.")
        return
    sent = failed = 0
    for uid in uids:
        try:
            await ctx.bot.send_message(chat_id=uid, text=f"📢 {text}")
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"✅ {sent}, ❌ {failed}")


# ─── Запуск ───────────────────────────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        raise ValueError("Укажи BOT_TOKEN!")
    if not ADMIN_ID:
        raise ValueError("Укажи ADMIN_ID!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("cancel",    cmd_cancel))
    app.add_handler(CommandHandler("language",  cmd_language))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    log.info("🚗 GarageLog Bot запущен")

    async def run():
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.info("Остановлен")

if __name__ == "__main__":
    main()
