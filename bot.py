"""
GarageLog Feedback Bot
Принимает сообщения от пользователей и пересылает их администратору.
"""

import os
import logging
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

# ─── Настройки ───────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")           # токен от @BotFather
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))       # твой Telegram user_id

# Состояния диалога
CHOOSING, TYPING_FEEDBACK, TYPING_BUG, TYPING_IDEA = range(4)

# ─── Логи ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ─── Хелперы ─────────────────────────────────────────────────────────────────

def username_str(user) -> str:
    name = user.full_name
    if user.username:
        name += f" (@{user.username})"
    return name


def now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🐛 Сообщить об ошибке", callback_data="bug")],
        [InlineKeyboardButton("💡 Предложить идею",    callback_data="idea")],
        [InlineKeyboardButton("💬 Общий отзыв",        callback_data="feedback")],
    ])


# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Привет! Это бот обратной связи *GarageLog* — приложения для ведения журнала обслуживания авто.\n\n"
        "Выбери, что хочешь сделать:",
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )
    return CHOOSING


# ─── Выбор типа ──────────────────────────────────────────────────────────────

async def choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()

    prompts = {
        "bug":      ("🐛", "Опишите ошибку как можно подробнее:\n• что делали\n• что ожидали\n• что произошло\n• устройство / браузер"),
        "idea":     ("💡", "Расскажите свою идею — что добавить или изменить в GarageLog?"),
        "feedback": ("💬", "Напишите свой отзыв — что нравится, что не нравится?"),
    }
    states = {"bug": TYPING_BUG, "idea": TYPING_IDEA, "feedback": TYPING_FEEDBACK}

    emoji, prompt = prompts[q.data]
    ctx.user_data["type"] = q.data
    ctx.user_data["emoji"] = emoji

    await q.edit_message_text(f"{emoji} {prompt}\n\nИли /cancel для отмены.")
    return states[q.data]


# ─── Приём сообщения ─────────────────────────────────────────────────────────

async def _receive(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text
    emoji = ctx.user_data.get("emoji", "💬")
    kind = ctx.user_data.get("type", "feedback")

    type_labels = {
        "bug":      "🐛 Ошибка",
        "idea":     "💡 Идея",
        "feedback": "💬 Отзыв",
    }
    label = type_labels.get(kind, "💬 Отзыв")

    # Пересылаем админу
    admin_msg = (
        f"{emoji} *Новое сообщение — {label}*\n"
        f"──────────────────\n"
        f"👤 {username_str(user)}\n"
        f"🆔 `{user.id}`\n"
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
        log.info("Forwarded %s from %s (%s)", kind, user.full_name, user.id)
    except Exception as e:
        log.error("Failed to forward to admin: %s", e)

    # Благодарим пользователя
    thanks = {
        "bug":      "✅ Спасибо! Мы разберёмся с ошибкой.",
        "idea":     "✅ Отличная идея! Возьмём в работу.",
        "feedback": "✅ Спасибо за отзыв! Это очень помогает.",
    }
    await update.message.reply_text(
        thanks.get(kind, "✅ Спасибо!") + "\n\nХочешь написать ещё что-то?",
        reply_markup=main_keyboard(),
    )
    return CHOOSING


# ─── Ответ от админа пользователю ────────────────────────────────────────────

async def admin_reply_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Админ нажал «Ответить» — сохраняем user_id и просим написать текст."""
    q = update.callback_query
    if update.effective_user.id != ADMIN_ID:
        await q.answer("⛔ Только для администратора.", show_alert=True)
        return

    _, user_id, user_name = q.data.split(":", 2)
    ctx.user_data["reply_to_id"] = int(user_id)
    ctx.user_data["reply_to_name"] = user_name

    await q.answer()
    await q.edit_message_reply_markup(None)
    await ctx.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"✏️ Напиши ответ для *{user_name}* (или /cancel):",
        parse_mode="Markdown",
    )


async def admin_reply_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Получаем текст ответа от админа и пересылаем пользователю."""
    if update.effective_user.id != ADMIN_ID:
        return
    if "reply_to_id" not in ctx.user_data:
        return

    user_id = ctx.user_data.pop("reply_to_id")
    user_name = ctx.user_data.pop("reply_to_name", "")
    reply_text = update.message.text

    try:
        await ctx.bot.send_message(
            chat_id=user_id,
            text=f"📨 *Ответ от разработчика GarageLog:*\n\n{reply_text}",
            parse_mode="Markdown",
        )
        await update.message.reply_text(f"✅ Ответ отправлен пользователю {user_name}.")
        log.info("Admin replied to user %s (%s)", user_name, user_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Не удалось отправить: {e}")


# ─── /cancel ─────────────────────────────────────────────────────────────────

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data.clear()
    await update.message.reply_text(
        "Отменено. Если понадоблюсь — просто напиши /start 🙂"
    )
    return ConversationHandler.END


# ─── /broadcast (только для админа) ─────────────────────────────────────────

async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда: /broadcast Текст сообщения — рассылает всем пользователям из файла users.txt."""
    if update.effective_user.id != ADMIN_ID:
        return

    if not ctx.args:
        await update.message.reply_text("Использование: /broadcast Текст сообщения")
        return

    text = " ".join(ctx.args)

    try:
        with open("users.txt") as f:
            user_ids = [int(line.strip()) for line in f if line.strip()]
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
        raise ValueError("Укажи BOT_TOKEN в переменных окружения!")
    if not ADMIN_ID:
        raise ValueError("Укажи ADMIN_ID в переменных окружения!")

    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler — пользователь пишет отзыв
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(choose, pattern="^(bug|idea|feedback)$")],
            TYPING_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, _receive)],
            TYPING_BUG:      [MessageHandler(filters.TEXT & ~filters.COMMAND, _receive)],
            TYPING_IDEA:     [MessageHandler(filters.TEXT & ~filters.COMMAND, _receive)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)

    # Ответ от админа пользователю
    app.add_handler(CallbackQueryHandler(admin_reply_start, pattern=r"^reply:\d+:.+"))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
            admin_reply_send,
        )
    )

    # Рассылка
    app.add_handler(CommandHandler("broadcast", broadcast))

    log.info("🚗 GarageLog Feedback Bot запущен")

    import asyncio

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
