"""
GarageLog Feedback Bot — multilingual
Языки: ru, en, zh, es, de, fr
Выбор языка: автоопределение + ручной выбор через /language
"""

import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))

# Состояния диалога
CHOOSING, TYPING_FEEDBACK, TYPING_BUG, TYPING_IDEA = range(4)

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ─── Переводы ────────────────────────────────────────────────────────────────

STRINGS = {
    "ru": {
        "welcome": (
            "👋 Привет! Это бот обратной связи *GarageLog* — "
            "приложения для ведения журнала обслуживания авто.\n\n"
            "Выбери, что хочешь сделать:"
        ),
        "btn_bug":      "🐛 Сообщить об ошибке",
        "btn_idea":     "💡 Предложить идею",
        "btn_feedback": "💬 Общий отзыв",
        "btn_language": "🌐 Язык / Language",
        "prompt_bug":   "🐛 Опишите ошибку подробнее:\n• что делали\n• что ожидали\n• что произошло\n• устройство / браузер",
        "prompt_idea":  "💡 Расскажите идею — что добавить или изменить в GarageLog?",
        "prompt_feedback": "💬 Напишите отзыв — что нравится, что нет?",
        "cancel_hint":  "\n\nИли /cancel для отмены.",
        "thanks_bug":      "✅ Спасибо! Разберёмся с ошибкой.",
        "thanks_idea":     "✅ Отличная идея! Возьмём в работу.",
        "thanks_feedback": "✅ Спасибо за отзыв! Это очень помогает.",
        "more":         "\n\nХочешь написать ещё что-то?",
        "cancelled":    "Отменено. Если понадоблюсь — напиши /start 🙂",
        "reply_from":   "📨 *Ответ от разработчика GarageLog:*\n\n",
        "label_bug":    "🐛 Ошибка",
        "label_idea":   "💡 Идея",
        "label_feedback": "💬 Отзыв",
        "choose_lang":  "🌐 Выбери язык:",
        "lang_set":     "✅ Язык изменён на Русский",
    },
    "en": {
        "welcome": (
            "👋 Hi! This is the *GarageLog* feedback bot — "
            "a car maintenance journal app.\n\n"
            "What would you like to do?"
        ),
        "btn_bug":      "🐛 Report a bug",
        "btn_idea":     "💡 Suggest an idea",
        "btn_feedback": "💬 General feedback",
        "btn_language": "🌐 Language",
        "prompt_bug":   "🐛 Please describe the bug:\n• what you did\n• what you expected\n• what happened\n• device / browser",
        "prompt_idea":  "💡 Tell us your idea — what to add or change in GarageLog?",
        "prompt_feedback": "💬 Share your feedback — what do you like or dislike?",
        "cancel_hint":  "\n\nOr /cancel to abort.",
        "thanks_bug":      "✅ Thanks! We'll look into the bug.",
        "thanks_idea":     "✅ Great idea! We'll consider it.",
        "thanks_feedback": "✅ Thanks for the feedback! It really helps.",
        "more":         "\n\nWant to send something else?",
        "cancelled":    "Cancelled. Feel free to write /start anytime 🙂",
        "reply_from":   "📨 *Reply from the GarageLog developer:*\n\n",
        "label_bug":    "🐛 Bug",
        "label_idea":   "💡 Idea",
        "label_feedback": "💬 Feedback",
        "choose_lang":  "🌐 Choose your language:",
        "lang_set":     "✅ Language set to English",
    },
    "zh": {
        "welcome": (
            "👋 你好！这是 *GarageLog* 反馈机器人 — "
            "汽车保养日志应用。\n\n"
            "请选择你想做的事："
        ),
        "btn_bug":      "🐛 报告错误",
        "btn_idea":     "💡 提出建议",
        "btn_feedback": "💬 综合反馈",
        "btn_language": "🌐 语言",
        "prompt_bug":   "🐛 请详细描述错误：\n• 你做了什么\n• 你期望发生什么\n• 实际发生了什么\n• 设备 / 浏览器",
        "prompt_idea":  "💡 请告诉我们你的想法 — 在 GarageLog 中添加或更改什么？",
        "prompt_feedback": "💬 请分享你的反馈 — 你喜欢或不喜欢什么？",
        "cancel_hint":  "\n\n或 /cancel 取消。",
        "thanks_bug":      "✅ 谢谢！我们会调查这个错误。",
        "thanks_idea":     "✅ 好主意！我们会考虑的。",
        "thanks_feedback": "✅ 感谢您的反馈！这非常有帮助。",
        "more":         "\n\n还想发送其他内容吗？",
        "cancelled":    "已取消。随时可以输入 /start 🙂",
        "reply_from":   "📨 *GarageLog 开发者的回复：*\n\n",
        "label_bug":    "🐛 错误",
        "label_idea":   "💡 建议",
        "label_feedback": "💬 反馈",
        "choose_lang":  "🌐 选择语言：",
        "lang_set":     "✅ 语言已设置为中文",
    },
    "es": {
        "welcome": (
            "👋 ¡Hola! Este es el bot de feedback de *GarageLog* — "
            "una app para llevar el diario de mantenimiento de tu coche.\n\n"
            "¿Qué quieres hacer?"
        ),
        "btn_bug":      "🐛 Reportar un error",
        "btn_idea":     "💡 Sugerir una idea",
        "btn_feedback": "💬 Feedback general",
        "btn_language": "🌐 Idioma",
        "prompt_bug":   "🐛 Describe el error con detalle:\n• qué hiciste\n• qué esperabas\n• qué pasó\n• dispositivo / navegador",
        "prompt_idea":  "💡 Cuéntanos tu idea — ¿qué añadir o cambiar en GarageLog?",
        "prompt_feedback": "💬 Comparte tu opinión — ¿qué te gusta o no te gusta?",
        "cancel_hint":  "\n\nO /cancel para cancelar.",
        "thanks_bug":      "✅ ¡Gracias! Investigaremos el error.",
        "thanks_idea":     "✅ ¡Buena idea! La tendremos en cuenta.",
        "thanks_feedback": "✅ ¡Gracias por el feedback! Es de gran ayuda.",
        "more":         "\n\n¿Quieres enviar algo más?",
        "cancelled":    "Cancelado. Escribe /start cuando quieras 🙂",
        "reply_from":   "📨 *Respuesta del desarrollador de GarageLog:*\n\n",
        "label_bug":    "🐛 Error",
        "label_idea":   "💡 Idea",
        "label_feedback": "💬 Feedback",
        "choose_lang":  "🌐 Elige tu idioma:",
        "lang_set":     "✅ Idioma establecido en Español",
    },
    "de": {
        "welcome": (
            "👋 Hallo! Dies ist der Feedback-Bot von *GarageLog* — "
            "einer App für dein Kfz-Wartungstagebuch.\n\n"
            "Was möchtest du tun?"
        ),
        "btn_bug":      "🐛 Fehler melden",
        "btn_idea":     "💡 Idee vorschlagen",
        "btn_feedback": "💬 Allgemeines Feedback",
        "btn_language": "🌐 Sprache",
        "prompt_bug":   "🐛 Bitte beschreibe den Fehler:\n• was du gemacht hast\n• was du erwartet hast\n• was passiert ist\n• Gerät / Browser",
        "prompt_idea":  "💡 Erzähl uns deine Idee — was soll in GarageLog hinzugefügt oder geändert werden?",
        "prompt_feedback": "💬 Teile dein Feedback — was gefällt dir, was nicht?",
        "cancel_hint":  "\n\nOder /cancel zum Abbrechen.",
        "thanks_bug":      "✅ Danke! Wir werden den Fehler untersuchen.",
        "thanks_idea":     "✅ Tolle Idee! Wir nehmen sie unter die Lupe.",
        "thanks_feedback": "✅ Danke für dein Feedback! Das hilft sehr.",
        "more":         "\n\nMöchtest du noch etwas senden?",
        "cancelled":    "Abgebrochen. Schreib /start, wann immer du möchtest 🙂",
        "reply_from":   "📨 *Antwort vom GarageLog-Entwickler:*\n\n",
        "label_bug":    "🐛 Fehler",
        "label_idea":   "💡 Idee",
        "label_feedback": "💬 Feedback",
        "choose_lang":  "🌐 Wähle deine Sprache:",
        "lang_set":     "✅ Sprache auf Deutsch gesetzt",
    },
    "fr": {
        "welcome": (
            "👋 Bonjour ! Ceci est le bot de retour d'expérience de *GarageLog* — "
            "une app pour tenir le journal d'entretien de votre voiture.\n\n"
            "Que souhaitez-vous faire ?"
        ),
        "btn_bug":      "🐛 Signaler un bug",
        "btn_idea":     "💡 Proposer une idée",
        "btn_feedback": "💬 Retour général",
        "btn_language": "🌐 Langue",
        "prompt_bug":   "🐛 Décrivez le bug en détail :\n• ce que vous avez fait\n• ce que vous attendiez\n• ce qui s'est passé\n• appareil / navigateur",
        "prompt_idea":  "💡 Partagez votre idée — que faut-il ajouter ou changer dans GarageLog ?",
        "prompt_feedback": "💬 Partagez votre avis — qu'est-ce qui vous plaît ou non ?",
        "cancel_hint":  "\n\nOu /cancel pour annuler.",
        "thanks_bug":      "✅ Merci ! Nous allons examiner ce bug.",
        "thanks_idea":     "✅ Bonne idée ! Nous allons y réfléchir.",
        "thanks_feedback": "✅ Merci pour votre retour ! C'est très utile.",
        "more":         "\n\nVoulez-vous envoyer autre chose ?",
        "cancelled":    "Annulé. Écrivez /start quand vous voulez 🙂",
        "reply_from":   "📨 *Réponse du développeur GarageLog :*\n\n",
        "label_bug":    "🐛 Bug",
        "label_idea":   "💡 Idée",
        "label_feedback": "💬 Retour",
        "choose_lang":  "🌐 Choisissez votre langue :",
        "lang_set":     "✅ Langue définie sur Français",
    },
}

LANG_MAP = {
    "ru": "ru", "be": "ru", "uk": "ru",
    "en": "en",
    "zh": "zh", "zh-hans": "zh", "zh-hant": "zh",
    "es": "es",
    "de": "de",
    "fr": "fr",
}

LANG_BUTTONS = [
    ("🇷🇺 Русский",    "lang:ru"),
    ("🇬🇧 English",    "lang:en"),
    ("🇨🇳 中文",        "lang:zh"),
    ("🇪🇸 Español",    "lang:es"),
    ("🇩🇪 Deutsch",    "lang:de"),
    ("🇫🇷 Français",   "lang:fr"),
]

# ─── Хелперы ─────────────────────────────────────────────────────────────────

def get_lang(user, ctx) -> str:
    """Язык: сначала смотрим на выбор пользователя, затем на Telegram-настройки."""
    if ctx.user_data.get("lang"):
        return ctx.user_data["lang"]
    code = (user.language_code or "en").lower().split("-")[0]
    return LANG_MAP.get(code, "en")

def t(user, ctx, key: str) -> str:
    lang = get_lang(user, ctx)
    return STRINGS.get(lang, STRINGS["en"])[key]

def username_str(user) -> str:
    name = user.full_name
    if user.username:
        name += f" (@{user.username})"
    return name

def now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")

def main_keyboard(user, ctx):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user, ctx, "btn_bug"),      callback_data="bug")],
        [InlineKeyboardButton(t(user, ctx, "btn_idea"),     callback_data="idea")],
        [InlineKeyboardButton(t(user, ctx, "btn_feedback"), callback_data="feedback")],
    ])

def lang_keyboard():
    rows = []
    for i in range(0, len(LANG_BUTTONS), 2):
        row = [InlineKeyboardButton(label, callback_data=cb)
               for label, cb in LANG_BUTTONS[i:i+2]]
        rows.append(row)
    return InlineKeyboardMarkup(rows)


# ─── Хэндлеры ────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        t(user, ctx, "welcome"),
        parse_mode="Markdown",
        reply_markup=main_keyboard(user, ctx),
    )
    return CHOOSING


async def show_langs(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Показываем кнопки выбора языка."""
    q = update.callback_query
    user = q.from_user
    await q.answer()
    try:
        await q.edit_message_text(
            t(user, ctx, "choose_lang"),
            reply_markup=lang_keyboard(),
        )
    except Exception:
        await ctx.bot.send_message(
            chat_id=user.id,
            text=t(user, ctx, "choose_lang"),
            reply_markup=lang_keyboard(),
        )
    return CHOOSING


async def set_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Пользователь выбрал язык."""
    q = update.callback_query
    user = q.from_user
    lang = q.data.split(":")[1]
    ctx.user_data["lang"] = lang
    await q.answer()
    await q.edit_message_text(
        STRINGS[lang]["lang_set"] + "\n\n" + STRINGS[lang]["welcome"],
        parse_mode="Markdown",
        reply_markup=main_keyboard(user, ctx),
    )
    return CHOOSING


async def choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    user = q.from_user
    await q.answer()

    key_map = {
        "bug":      ("prompt_bug",      TYPING_BUG),
        "idea":     ("prompt_idea",     TYPING_IDEA),
        "feedback": ("prompt_feedback", TYPING_FEEDBACK),
    }
    emoji_map = {"bug": "🐛", "idea": "💡", "feedback": "💬"}

    prompt_key, state = key_map[q.data]
    ctx.user_data["type"]  = q.data
    ctx.user_data["emoji"] = emoji_map[q.data]

    await q.edit_message_text(t(user, ctx, prompt_key) + t(user, ctx, "cancel_hint"))
    return state


async def _receive(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user  = update.effective_user
    text  = update.message.text
    emoji = ctx.user_data.get("emoji", "💬")
    kind  = ctx.user_data.get("type", "feedback")
    lang  = get_lang(user, ctx)

    label_key = {"bug": "label_bug", "idea": "label_idea", "feedback": "label_feedback"}
    label = STRINGS.get(lang, STRINGS["en"])[label_key.get(kind, "label_feedback")]

    admin_msg = (
        f"{emoji} *Новое сообщение — {label}*\n"
        f"──────────────────\n"
        f"👤 {username_str(user)}\n"
        f"🆔 `{user.id}`\n"
        f"🌐 `{lang}` (tg: `{user.language_code}`)\n"
        f"🕐 {now()}\n"
        f"──────────────────\n"
        f"{text}"
    )
    reply_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Ответить", callback_data=f"reply:{user.id}:{user.full_name}")]
    ])

    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_msg,
            parse_mode="Markdown",
            reply_markup=reply_kb,
        )
    except Exception as e:
        log.error("Failed to forward: %s", e)

    thanks_key = {"bug": "thanks_bug", "idea": "thanks_idea", "feedback": "thanks_feedback"}
    await update.message.reply_text(
        t(user, ctx, thanks_key.get(kind, "thanks_feedback")) + t(user, ctx, "more"),
        reply_markup=main_keyboard(user, ctx),
    )
    return CHOOSING


async def admin_reply_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if update.effective_user.id != ADMIN_ID:
        await q.answer("⛔ Только для администратора.", show_alert=True)
        return
    _, user_id, user_name = q.data.split(":", 2)
    ctx.user_data["reply_to_id"]   = int(user_id)
    ctx.user_data["reply_to_name"] = user_name
    await q.answer()
    await q.edit_message_reply_markup(None)
    await ctx.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"✏️ Напиши ответ для *{user_name}* (или /cancel):",
        parse_mode="Markdown",
    )


async def admin_reply_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return
    if "reply_to_id" not in ctx.user_data:
        return
    user_id   = ctx.user_data.pop("reply_to_id")
    user_name = ctx.user_data.pop("reply_to_name", "")
    try:
        await ctx.bot.send_message(
            chat_id=user_id,
            text=f"📨 *Reply from GarageLog developer:*\n\n{update.message.text}",
            parse_mode="Markdown",
        )
        await update.message.reply_text(f"✅ Ответ отправлен: {user_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Не удалось: {e}")


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    ctx.user_data.pop("type", None)
    ctx.user_data.pop("emoji", None)
    await update.message.reply_text(
        t(user, ctx, "cancelled"),
        reply_markup=main_keyboard(user, ctx),
    )
    return CHOOSING


async def language_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Команда /language — показывает выбор языка."""
    user = update.effective_user
    await update.message.reply_text(
        t(user, ctx, "choose_lang"),
        reply_markup=lang_keyboard(),
    )
    return CHOOSING


async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return
    if not ctx.args:
        await update.message.reply_text("Использование: /broadcast Текст")
        return
    text = " ".join(ctx.args)
    try:
        with open("users.txt") as f:
            user_ids = [int(l.strip()) for l in f if l.strip()]
    except FileNotFoundError:
        await update.message.reply_text("Файл users.txt не найден.")
        return
    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await ctx.bot.send_message(chat_id=uid, text=f"📢 {text}")
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"✅ Отправлено: {sent}, ❌ Ошибок: {failed}")


# ─── Запуск ──────────────────────────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        raise ValueError("Укажи BOT_TOKEN!")
    if not ADMIN_ID:
        raise ValueError("Укажи ADMIN_ID!")

    app = Application.builder().token(BOT_TOKEN).build()

    # show_langs и set_lang регистрируем ПЕРВЫМИ (до ConversationHandler)
    # чтобы они перехватывали callback до того как ConversationHandler их проигнорирует
    app.add_handler(CallbackQueryHandler(show_langs, pattern="^show_langs$"), group=0)
    app.add_handler(CallbackQueryHandler(set_lang,   pattern="^lang:"),       group=0)

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("language", language_cmd),
        ],
        states={
            CHOOSING: [
                CallbackQueryHandler(choose,     pattern="^(bug|idea|feedback)$"),
                CallbackQueryHandler(show_langs, pattern="^show_langs$"),
                CallbackQueryHandler(set_lang,   pattern="^lang:"),
            ],
            TYPING_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _receive),
                CallbackQueryHandler(show_langs, pattern="^show_langs$"),
                CallbackQueryHandler(set_lang,   pattern="^lang:"),
            ],
            TYPING_BUG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _receive),
                CallbackQueryHandler(show_langs, pattern="^show_langs$"),
                CallbackQueryHandler(set_lang,   pattern="^lang:"),
            ],
            TYPING_IDEA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _receive),
                CallbackQueryHandler(show_langs, pattern="^show_langs$"),
                CallbackQueryHandler(set_lang,   pattern="^lang:"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("language", language_cmd),
            CallbackQueryHandler(show_langs, pattern="^show_langs$"),
            CallbackQueryHandler(set_lang,   pattern="^lang:"),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv, group=1)
    app.add_handler(CallbackQueryHandler(admin_reply_start, pattern=r"^reply:\d+:.+"), group=0)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
            admin_reply_send,
        )
    )
    app.add_handler(CommandHandler("broadcast", broadcast))

    log.info("🚗 GarageLog Feedback Bot (multilingual) запущен")

    async def run():
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.info("Бот остановлен")


if __name__ == "__main__":
    main()
