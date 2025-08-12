from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultVideo
from aiogram.enums.parse_mode import ParseMode
import sys
from services import rule34_service, danbooru_service, safebooru_service, konachan_service

sys.path.append("..")
router = Router()

ITEMS_PER_PAGE = 50

@router.inline_query(F.query.contains("vid"))
async def show_user_videos(inline_query: InlineQuery):
    result = []
    offset = int(inline_query.offset) if inline_query.offset else 0
    page = offset + 1

    try:
        parts = inline_query.query.split(" ")
        if len(parts) < 2:
            await inline_query.answer([], is_personal=True)
            return

        service = parts[1]
        tags = inline_query.query.split(f"vid {service}", 1)[-1].strip()

        if service == "r34":
            response_data = await rule34_service.get_post_list(tags + " animated", limit=ITEMS_PER_PAGE, page=page)
        elif service == "danbooru":
            response_data = await danbooru_service.get_post_list(tags, limit=ITEMS_PER_PAGE, page=page)
        elif service == "safebooru":
            response_data = await safebooru_service.get_post_list(tags + " animated", limit=ITEMS_PER_PAGE, page=page)
        elif service == "kona":
            response_data = await konachan_service.get_post_list(tags + " animated", limit=ITEMS_PER_PAGE, page=page)
        else:
            response_data = []

        if response_data:
            for idx, item in enumerate(response_data):
                file_url = item.get("file_url")
                if not file_url:
                    continue

                if service == "r34":
                    thumb = item.get("preview_url")
                    src = f"[Source](https://rule34.xxx/index.php?page=post&s=view&id={item.get('id')})"
                    uid = f"{item.get('hash')}_{page}_{idx}"
                    width = item.get("width")
                    height = item.get("height")
                    duration = item.get("duration")
                elif service == "danbooru":
                    thumb = item.get("preview_file_url")
                    src = f"[Source](https://danbooru.donmai.us/posts/{item.get('id')})"
                    uid = f"{item.get('md5')}_{page}_{idx}"
                    width = item.get("image_width")
                    height = item.get("image_height")
                    duration = item.get("duration")
                elif service == "safebooru":
                    thumb = item.get("preview_url")
                    src = f"[Source](https://safebooru.org/index.php?page=post&s=view&id={item.get('id')})"
                    uid = f"{item.get('hash')}_{page}_{idx}"
                    width = item.get("width")
                    height = item.get("height")
                    duration = item.get("duration")
                elif service == "kona":
                    thumb = item.get("preview_url")
                    src = f"[Source](https://konachan.com/post/show/{item.get('id')})"
                    uid = f"{item.get('md5')}_{page}_{idx}"
                    width = item.get("width")
                    height = item.get("height")
                    duration = item.get("duration")

                result.append(
                    InlineQueryResultVideo(
                        id=uid,
                        video_url=file_url,
                        mime_type="video/mp4",
                        thumbnail_url=thumb,
                        title=f"{service.capitalize()} Video",
                        parse_mode=ParseMode.MARKDOWN_V2,
                        caption=src,
                        video_width=width,
                        video_height=height,
                        video_duration=duration,
                        description=tags
                    )
                )

    except Exception as e:
        print(f"An error occurred while processing the inline query: {e}")

    next_offset = str(offset + 1) if response_data else ""

    await inline_query.answer(
        results=result,
        is_personal=True,
        cache_time=0,
        next_offset=next_offset
    )
