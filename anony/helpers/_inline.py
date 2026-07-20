# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

from pyrogram import types

# Handle different Pyrogram versions for ButtonStyle
try:
    from pyrogram.enums import ButtonStyle
except ImportError:
    try:
        from pyrogram.types import ButtonStyle
    except ImportError:
        # Fallback for older Pyrogram versions
        class ButtonStyle:
            PRIMARY = 0
            SUCCESS = 1
            DANGER = 2
            DEFAULT = 3

from anony import app, config, lang
from anony.core.lang import lang_codes

class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

        # --- PREMIUM START MESSAGE (Enhanced) ---
        self.START_TEXT = (
            "✨ **ɢʀᴇᴇᴛɪɴɢs {mention} !** ✨\n\n"
            "🎵 **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {bot_name}** 🚀\n\n"
            "──────────────────────────────\n"
            "🎧 **ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀғᴜʟ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ**\n"
            "**ᴡɪᴛʜ ᴜʟᴛʀᴀ-ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴀᴜᴅɪᴏ sᴜᴘᴘᴏʀᴛ.**\n\n"
            "🔹 **ᴘʟᴀʏ sᴏɴɢs ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ & sᴘᴏᴛɪғʏ**\n"
            "🔹 **ʟᴀɢ-ғʀᴇᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇxᴘᴇʀɪᴇɴᴄᴇ**\n"
            "🔹 **ᴀᴅᴍɪɴ ᴄᴏɴᴛʀᴏʟs & ᴍᴜʟᴛɪ-ʟᴀɴɢᴜᴀɢᴇ**\n"
            "──────────────────────────────\n\n"
            "📢 **ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ sᴛᴀʀᴛ**\n"
            "**ᴇɴᴊᴏʏɪɴɢ ᴛʜᴇ ᴍᴜsɪᴄ ᴡɪᴛʜ ʏᴏᴜʀ ғʀɪᴇɴᴅs!** 🎉"
        )

    def _btn(self, text: str, **kwargs) -> types.InlineKeyboardButton:
        """Helper to create consistently styled buttons."""
        return self.ikb(text=text, **kwargs)

    def _owner_link(self) -> str:
        """Return correct deep link for OWNER_ID (numeric or username)."""
        owner = str(config.OWNER_ID).strip()
        if owner.startswith("@"):
            # Username -> use resolve link
            return f"tg://resolve?domain={owner.lstrip('@')}"
        else:
            # Numeric ID -> use openmessage
            return f"tg://openmessage?user_id={owner}"

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [[self._btn(f"✕  {text}", callback_data="cancel_dl", style=ButtonStyle.DANGER)]]
        )

    def controls(self, chat_id: int, status: str = None, timer: str = None, remove: bool = False):
        keyboard = []

        if status:
            keyboard.append(
                [self._btn(f"📊  {status}", callback_data=f"controls status {chat_id}", style=ButtonStyle.DEFAULT)]
            )
        elif timer:
            keyboard.append(
                [self._btn(f"⏳  {timer}", callback_data=f"controls status {chat_id}", style=ButtonStyle.DEFAULT)]
            )

        if not remove:
            keyboard.append(
                [
                    self._btn("▶️", callback_data=f"controls resume {chat_id}", style=ButtonStyle.SUCCESS),
                    self._btn("⏸", callback_data=f"controls pause {chat_id}", style=ButtonStyle.PRIMARY),
                    self._btn("⏭", callback_data=f"controls skip {chat_id}", style=ButtonStyle.PRIMARY),
                    self._btn("🔄", callback_data=f"controls replay {chat_id}", style=ButtonStyle.SUCCESS),
                    self._btn("⏹", callback_data=f"controls stop {chat_id}", style=ButtonStyle.DANGER),
                ]
            )
            # यहाँ Autoplay का बटन जोड़ दिया गया है जो सीधे प्लगइन से जुड़ा है
            keyboard.append(
                [
                    self._btn("🔁  Autoplay", callback_data=f"toggle_autoplay_{chat_id}", style=ButtonStyle.PRIMARY)
                ]
            )

        return self.ikm(keyboard)

    def help_markup(self, _lang: dict, back: bool = False):
        if back:
            rows = [
                [
                    self._btn("⬅️  Back", callback_data="help back", style=ButtonStyle.PRIMARY),
                    self._btn("🗑  Close", callback_data="help close", style=ButtonStyle.DANGER),
                ]
            ]
        else:
            cbs = ["admins", "auth", "blist", "lang", "ping", "play", "queue", "stats", "sudo"]
            buttons = [
                self._btn(f"▸  {_lang[f'help_{i}'].upper()}", callback_data=f"help {cb}", style=ButtonStyle.PRIMARY)
                for i, cb in enumerate(cbs)
            ]
            rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

        return self.ikm(rows)

    def lang_markup(self, _lang: str):
        langs = lang.get_languages()

        buttons = [
            self._btn(
                f"🌍  {name}  {'✓' if code == _lang else '  '}",
                callback_data=f"lang_change {code}",
                style=ButtonStyle.SUCCESS if code == _lang else ButtonStyle.PRIMARY
            )
            for code, name in langs.items()
        ]

        rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    def ping_markup(self, text: str):
        support = str(config.SUPPORT_CHAT)
        url = support if "t.me" in support or "tg://" in support else f"tg://user?id={support}"
        return self.ikm(
            [[self._btn(f"🌐  {text}", url=url, style=ButtonStyle.SUCCESS)]]
        )

    def play_queued(self, chat_id: int, item_id: str, _text: str):
        return self.ikm(
            [[self._btn(f"▶️  {_text}", callback_data=f"controls force {chat_id} {item_id}", style=ButtonStyle.SUCCESS)]]
        )

    def queue_markup(self, chat_id: int, _text: str, playing: bool):
        action = "pause" if playing else "resume"
        icon = "⏸" if playing else "▶️"
        return self.ikm(
            [[self._btn(f"{icon}  {_text}", callback_data=f"controls {action} {chat_id} q", style=ButtonStyle.PRIMARY)]]
        )

    def settings_markup(self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int):
        return self.ikm(
            [
                [
                    self._btn(f"🛠  {lang['play_mode']}", callback_data="settings", style=ButtonStyle.DEFAULT),
                    self._btn(f"{'🔒' if admin_only else '🔓'}", callback_data="settings play", style=ButtonStyle.SUCCESS),
                ],
                [
                    self._btn(f"🗑  {lang['cmd_delete']}", callback_data="settings", style=ButtonStyle.DEFAULT),
                    self._btn(f"{'✅' if cmd_delete else '❌'}", callback_data="settings delete", style=ButtonStyle.PRIMARY),
                ],
                [
                    self._btn(f"🌐  {lang['language']}", callback_data="settings", style=ButtonStyle.DEFAULT),
                    self._btn(f"🚩  {lang_codes[language]}", callback_data="language", style=ButtonStyle.SUCCESS),
                ],
            ]
        )

    def start_key(self, lang: dict, private: bool = False):
        # Owner link (safe for both ID and username)
        owner_link = self._owner_link()

        # Support / channel links with fallback
        sup_chat = str(config.SUPPORT_CHAT)
        if "t.me" not in sup_chat and "tg://" not in sup_chat:
            sup_chat = f"tg://user?id={sup_chat}"

        sup_channel = str(config.SUPPORT_CHANNEL)
        if "t.me" not in sup_channel and "tg://" not in sup_channel:
            sup_channel = f"tg://user?id={sup_channel}"

        # Base rows
        rows = [
            [
                self._btn(
                    "➕  Add Me To Your Group  ➕",
                    url=f"https://t.me/{app.username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                )
            ],
            [
                self._btn("📜  Help", callback_data="help", style=ButtonStyle.PRIMARY),
                self._btn("👤  Owner", url=owner_link, style=ButtonStyle.PRIMARY),
            ],
            [
                self._btn("💬  Support", url=sup_chat, style=ButtonStyle.PRIMARY),
                self._btn("📢  Updates", url=sup_channel, style=ButtonStyle.PRIMARY),
            ],
        ]

        if private:
            rows.append(
                [
                    self._btn(
                        "📁  Source Code",
                        url="t.me/link_buyer",
                        style=ButtonStyle.DANGER,
                    )
                ]
            )
        else:
            rows.append(
                [
                    self._btn(
                        "🚩  Language",
                        callback_data="language",
                        style=ButtonStyle.SUCCESS,
                    )
                ]
            )

        return self.ikm(rows)

    def yt_key(self, link: str):
        return self.ikm(
            [
                [
                    self._btn("🔗  Copy Link", copy_text=link, style=ButtonStyle.PRIMARY),
                    self._btn("🎬  Watch on YT", url=link, style=ButtonStyle.DANGER),
                ]
            ]
        )
