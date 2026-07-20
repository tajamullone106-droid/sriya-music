# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

from pyrogram import filters
from pyrogram.types import CallbackQuery
from anony import app

# यह डिक्शनरी याद रखेगी कि किस ग्रुप (chat_id) में Autoplay ON है और किसमें OFF
autoplay_chats = {}

@app.on_callback_query(filters.regex("^toggle_autoplay_"))
async def toggle_autoplay_cb(client, CallbackQuery: CallbackQuery):
    # Callback data से chat_id निकालना
    try:
        chat_id = int(CallbackQuery.data.split("_")[2])
    except Exception:
        return await CallbackQuery.answer("Error!", show_alert=True)

    # चेक करें कि इस ग्रुप में पहले से Autoplay ON है या नहीं
    is_on = autoplay_chats.get(chat_id, False)

    if is_on:
        # अगर ON है, तो उसे OFF कर दें
        autoplay_chats[chat_id] = False
        await CallbackQuery.answer("Autoplay OFF ❌ कर दिया गया है!", show_alert=True)
    else:
        # अगर OFF है, तो उसे ON कर दें
        autoplay_chats[chat_id] = True
        await CallbackQuery.answer("Autoplay ON 🔁 कर दिया गया है!", show_alert=True)

