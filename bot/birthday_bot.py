"""Utilities for sending birthday congratulations to a Telegram chat."""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import List, Sequence

import requests


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BIRTHDAYS_PATH = DATA_DIR / "birthdays.json"
MESSAGES_PATH = DATA_DIR / "messages.json"


class BirthdayBotError(Exception):
    """Base exception for the birthday bot."""


class MissingEnvironmentVariableError(BirthdayBotError):
    """Raised when an expected environment variable is missing."""

    def __init__(self, variable: str) -> None:
        super().__init__(f"Environment variable {variable!r} is required but missing.")
        self.variable = variable


class TelegramApiError(BirthdayBotError):
    """Raised when the Telegram API returns an error."""

    def __init__(self, status_code: int, response_text: str) -> None:
        super().__init__(
            f"Telegram API request failed with status {status_code}: {response_text}"
        )
        self.status_code = status_code
        self.response_text = response_text


@dataclass(frozen=True)
class Person:
    """Represents a person with a birthday."""

    name: str
    nickname: str
    birthday: date

    @property
    def mention(self) -> str:
        """Return a Telegram mention string using the nickname."""
        nick = self.nickname.strip()
        if nick.startswith("@"):
            return nick
        return f"@{nick}"


@dataclass(frozen=True)
class MessageTemplate:
    """A template message for congratulating a person."""

    text: str

    def render(self, person: Person) -> str:
        """Fill in the template with the person's information."""
        return self.text.format(name=person.name, mention=person.mention)


def load_birthdays(path: Path = BIRTHDAYS_PATH) -> List[Person]:
    """Load birthday data from the provided JSON path."""
    with path.open("r", encoding="utf-8") as f:
        entries = json.load(f)

    people: List[Person] = []
    for entry in entries:
        try:
            birthday = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            people.append(
                Person(
                    name=entry["name"].strip(),
                    nickname=entry["nickname"].strip(),
                    birthday=birthday,
                )
            )
        except KeyError as exc:
            raise BirthdayBotError(
                f"Birthday entry {entry!r} is missing required field {exc.args[0]!r}."
            ) from exc
    return people


def load_message_templates(path: Path = MESSAGES_PATH) -> List[MessageTemplate]:
    """Load message templates from JSON."""
    with path.open("r", encoding="utf-8") as f:
        entries = json.load(f)

    return [MessageTemplate(text=entry.strip()) for entry in entries if entry.strip()]


def select_messages(
    people: Sequence[Person], templates: Sequence[MessageTemplate]
) -> List[str]:
    """Select a random template for each person and render it."""
    if not templates:
        raise BirthdayBotError("No message templates available.")

    messages: List[str] = []
    for person in people:
        template = random.choice(templates)
        messages.append(template.render(person))
    return messages


def _get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise MissingEnvironmentVariableError(name)
    return value


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Send a message via the Telegram Bot API."""
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=30,
    )
    if response.status_code >= 400:
        raise TelegramApiError(response.status_code, response.text)


def congratulate_today(
    *,
    today: date | None = None,
    birthdays_path: Path = BIRTHDAYS_PATH,
    messages_path: Path = MESSAGES_PATH,
) -> List[str]:
    """Send congratulations for all birthdays occurring today.

    Returns the list of messages that were successfully sent. This is primarily
    intended for logging and testing purposes.
    """

    today = today or date.today()
    people = load_birthdays(birthdays_path)
    templates = load_message_templates(messages_path)

    celebrants = [
        person
        for person in people
        if person.birthday.month == today.month and person.birthday.day == today.day
    ]

    if not celebrants:
        return []

    token = _get_env_variable("TELEGRAM_BOT_TOKEN")
    chat_id = _get_env_variable("TELEGRAM_CHAT_ID")

    messages = select_messages(celebrants, templates)
    for message in messages:
        send_telegram_message(token, chat_id, message)
    return messages


__all__ = [
    "BirthdayBotError",
    "MissingEnvironmentVariableError",
    "TelegramApiError",
    "Person",
    "MessageTemplate",
    "congratulate_today",
    "load_birthdays",
    "load_message_templates",
    "select_messages",
]
