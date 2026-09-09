# GarageLog Feedback Bot 🚗

Telegram-бот для сбора обратной связи от пользователей GarageLog.

## Что умеет

| Функция | Описание |
|---|---|
| 🐛 Ошибки | Пользователь описывает баг, бот пересылает тебе |
| 💡 Идеи | Предложения по фичам |
| 💬 Отзыв | Общие впечатления |
| ↩️ Ответить | Ты нажимаешь кнопку под сообщением и отвечаешь прямо из Telegram |
| 📢 Рассылка | `/broadcast Текст` — отправляет всем пользователям |

---

## Быстрый старт

### 1. Создай бота
Напиши [@BotFather](https://t.me/BotFather):
```
/newbot
```
Получи **BOT_TOKEN**.

### 2. Узнай свой Telegram ID
Напиши [@userinfobot](https://t.me/userinfobot) — получи **ADMIN_ID**.

### 3. Настрой переменные
```bash
cp .env.example .env
# Вставь BOT_TOKEN и ADMIN_ID в .env
```

---

## Запуск

### Вариант A — Docker (рекомендуется, для сервера)
```bash
docker compose up -d
docker compose logs -f   # смотреть логи
```

### Вариант B — Локально (для разработки)
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

### Вариант C — Systemd (VPS, без Docker)
Создай `/etc/systemd/system/garagelog-bot.service`:
```ini
[Unit]
Description=GarageLog Feedback Bot
After=network.target

[Service]
WorkingDirectory=/opt/garagelog-feedback-bot
EnvironmentFile=/opt/garagelog-feedback-bot/.env
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable --now garagelog-bot
sudo journalctl -u garagelog-bot -f
```

---

## Как добавить ссылку в GarageLog

В настройках приложения (`app/settings/page.tsx`) замени placeholder:

```tsx
<a href="https://t.me/ВАШ_БОТ" target="_blank"
  className="w-full flex items-center justify-between px-4 py-4 border-b border-[#333333]">
  <div className="flex items-center gap-3">
    <span className="text-xl">✈️</span>
    <div>
      <p className="text-white font-semibold">Написать автору</p>
      <p className="text-[#888888] text-xs">Обратная связь в Telegram</p>
    </div>
  </div>
  <span className="text-[#888888]">→</span>
</a>
```

---

## Команды бота

| Команда | Кто может | Описание |
|---|---|---|
| `/start` | все | Начать диалог |
| `/cancel` | все | Отменить текущий ввод |
| `/broadcast Текст` | только админ | Разослать всем пользователям |
