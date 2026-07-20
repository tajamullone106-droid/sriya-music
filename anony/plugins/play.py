# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

from pathlib import Path

from pyrogram import filters, types

from anony import anon, app, config, db, lang, queue, tg, yt
from anony.helpers import buttons, utils
from anony.helpers._play import checkUB


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text

@app.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    sent = await m.reply_text(m.lang["play_searching"])
    
    try:
        await m.delete()
    except:
        pass

    file = None
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []

    try:
        if media:
            setattr(sent, "lang", m.lang)
            file = await tg.download(m.reply_to_message, sent)

        elif m3u8:
            file = await tg.process_m3u8(url, sent.id, video)

        elif url:
            if "playlist" in url:
                await sent.edit_text(m.lang["playlist_fetch"])
                tracks = await yt.playlist(
                    config.PLAYLIST_LIMIT, mention, url, video
                )

                if not tracks:
                    return await sent.edit_text(m.lang["playlist_error"])

                file = tracks[0]
                tracks.remove(file)
                file.message_id = sent.id
            else:
                # URL के लिए details() use करें
                details = await yt.details(url)
                if details:
                    title, duration_min, duration_sec, thumbnail, vidid = details
                    # एक simple object बनाएं
                    class Track:
                        pass
                    file = Track()
                    file.id = vidid
                    file.title = title
                    file.duration = duration_min
                    file.duration_sec = duration_sec
                    file.thumbnail = thumbnail
                    file.url = url if "youtube" in url else f"https://youtube.com/watch?v={vidid}"
                    file.message_id = sent.id
                else:
                    file = None

            if not file:
                return await sent.edit_text(
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )

        elif len(m.command) >= 2:
            query = " ".join(m.command[1:])
            
            # Query search के लिए py_yt का VideosSearch use करें
            from py_yt import VideosSearch
            search = VideosSearch(query, limit=1)
            results = await search.next()
            
            if results and results.get("result"):
                result = results["result"][0]
                vidid = result["id"]
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                yt_url = result["link"]
                
                # Duration calculate करें
                duration_sec = 0
                if duration_min:
                    try:
                        parts = duration_min.split(":")
                        if len(parts) == 3:
                            duration_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
                        elif len(parts) == 2:
                            duration_sec = int(parts[0])*60 + int(parts[1])
                        else:
                            duration_sec = int(parts[0])
                    except:
                        duration_sec = 0
                
                # Object बनाएं
                class Track:
                    pass
                file = Track()
                file.id = vidid
                file.title = title
                file.duration = duration_min
                file.duration_sec = duration_sec
                file.thumbnail = thumbnail
                file.url = yt_url
                file.message_id = sent.id
            else:
                file = None
                
            if not file:
                return await sent.edit_text(
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )

        if not file:
            return await sent.edit_text(m.lang["play_usage"])

        if file.duration_sec > config.DURATION_LIMIT:
            return await sent.edit_text(
                m.lang["play_duration_limit"].format(config.DURATION_LIMIT // 60)
            )

        if await db.is_logger():
            await utils.play_log(m, sent.link, file.title, file.duration)

        file.user = mention
        if force:
            queue.force_add(m.chat.id, file)
        else:
            position = queue.add(m.chat.id, file)

            if position != 0 or await db.get_call(m.chat.id):
                await sent.edit_text(
                    m.lang["play_queued"].format(
                        position,
                        file.url,
                        file.title,
                        file.duration,
                        m.from_user.mention,
                    ),
                    reply_markup=buttons.play_queued(
                        m.chat.id, file.id, m.lang["play_now"]
                    ),
                )
                if tracks:
                    added = playlist_to_queue(m.chat.id, tracks)
                    await app.send_message(
                        chat_id=m.chat.id,
                        text=m.lang["playlist_queued"].format(len(tracks)) + added,
                    )
                return

        if not file.file_path if hasattr(file, 'file_path') else True:
            fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
            if Path(fname).exists():
                file.file_path = fname
            else:
                await sent.edit_text(m.lang["play_downloading"])
                downloaded_path, success = await yt.download(file.id, sent, video=video)
                if success and downloaded_path:
                    file.file_path = downloaded_path
                else:
                    return await sent.edit_text("❌ डाउनलोड फेल हो गया।")

        await anon.play_media(chat_id=m.chat.id, message=sent, media=file)
        if not tracks:
            return
        added = playlist_to_queue(m.chat.id, tracks)
        await app.send_message(
            chat_id=m.chat.id,
            text=m.lang["playlist_queued"].format(len(tracks)) + added,
        )
        
    except Exception as e:
        await sent.edit_text(f"❌ Error: {str(e)[:200]}")
        print(f"Play Error: {e}")
