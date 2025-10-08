"""Entry point for running the Telegram birthday bot."""
from bot.birthday_bot import BirthdayBotError, congratulate_today


def main() -> None:
    try:
        messages = congratulate_today()
    except BirthdayBotError as exc:
        raise SystemExit(str(exc))

    if messages:
        print("Sent the following birthday messages:")
        for message in messages:
            print(f"- {message}")
    else:
        print("No birthdays today.")


if __name__ == "__main__":
    main()
