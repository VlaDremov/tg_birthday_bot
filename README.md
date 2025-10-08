# Telegram Birthday Bot

This repository contains a simple Telegram bot that congratulates members of a group on their birthdays. The bot is designed to be executed once per day—via GitHub Actions or manually—to check if anyone has a birthday and send a celebratory message to the configured Telegram chat.

## How it works

1. **Birthday data** lives in [`data/birthdays.json`](data/birthdays.json). Each entry contains a name, Telegram nickname, and birth date.
2. **Message templates** are defined in [`data/messages.json`](data/messages.json). A random template is chosen for every celebrant so greetings stay fresh.
3. **Execution** happens through [`main.py`](main.py), which loads the data, determines who is celebrating today, and sends messages through the Telegram Bot API.
4. **Automation** is handled by the GitHub Actions workflow defined in [`.github/workflows/birthday.yml`](.github/workflows/birthday.yml). It is scheduled to run every day at 07:00 UTC and can also be triggered manually.

## Configuration

Before running the bot you need to provide:

- `TELEGRAM_BOT_TOKEN` – the token of your Telegram bot obtained from [@BotFather](https://t.me/BotFather).
- `TELEGRAM_CHAT_ID` – the numeric ID of the chat (group, supergroup, or channel) where the bot should post birthday wishes.

When using GitHub Actions, add both values as **repository secrets** with the same names. You can do this from your GitHub
repository by navigating to `Settings` → `Secrets and variables` → `Actions`, clicking **New repository secret**, and creating
secrets named `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. The scheduled workflow will automatically read these values and
expose them to the bot when it runs.

To customize the people or the greetings, edit the JSON files under the `data/` directory. Birthday dates must be in `YYYY-MM-DD` format.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=your-bot-token
export TELEGRAM_CHAT_ID=your-chat-id
python main.py
```

If someone in the list has their birthday today, the bot will send a message and print the contents to the console. Otherwise, it will simply report that there are no birthdays.
