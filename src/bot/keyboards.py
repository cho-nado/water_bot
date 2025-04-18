# src/bot/keyboards.py
"""
Клавиатуры для главного меню, настроек и напоминаний.
"""
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="💧 200 ml"), KeyboardButton(text="💧💧 350 ml")],
        [KeyboardButton(text="📊 Check Progress"), KeyboardButton(text="⏰ Reminders")],
        [KeyboardButton(text="⚙ Settings"), KeyboardButton(text="💵 Subscription")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def reminder_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🕐 Add Reminders")],
        [KeyboardButton(text="📋 Show Reminders")],
        [KeyboardButton(text="🗑️ Delete All")],
        [KeyboardButton(text="✂️ Delete Specific")],
        [KeyboardButton(text="⬅️ Back")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def settings_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🌍 Time zone")],
        [KeyboardButton(text="⬅️ Back")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def timezone_menu(current_tz: str | None = None) -> InlineKeyboardMarkup:
    zones = [
        ("UTC−12:00", "Etc/GMT+12"),
        ("UTC−09:00 (Alaska)", "America/Anchorage"),
        ("UTC−08:00 (LA)", "America/Los_Angeles"),
        ("UTC−05:00 (New York)", "America/New_York"),
        ("UTC+00:00 (London)", "Europe/London"),
        ("UTC+01:00 (Berlin)", "Europe/Berlin"),
        ("UTC+02:00 (Helsinki)", "Europe/Helsinki"),
        ("UTC+03:00 (Moscow)", "Europe/Moscow"),
        ("UTC+04:00 (Baku)", "Asia/Baku"),
        ("UTC+05:00 (Tashkent)", "Asia/Tashkent"),
        ("UTC+05:30 (India)", "Asia/Kolkata"),
        ("UTC+06:00 (Almaty)", "Asia/Almaty"),
        ("UTC+07:00 (Bangkok)", "Asia/Bangkok"),
        ("UTC+08:00 (Beijing)", "Asia/Shanghai"),
        ("UTC+09:00 (Tokyo)", "Asia/Tokyo"),
        ("UTC+10:00 (Sydney)", "Australia/Sydney"),
        ("UTC+12:00 (Auckland)", "Pacific/Auckland")
    ]
    buttons: list[list[InlineKeyboardButton]] = []
    for name, code in zones:
        prefix = "✅ " if code == current_tz else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{prefix}{name}",
                callback_data=f"tz_{code}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Back",
            callback_data="settings_menu"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscription_menu() -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text="⬅️ Back")]]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
