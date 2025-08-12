import random
import sys
import re
import aiohttp
from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.markdown import hlink
from aiogram.types import (
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultGif,
    InlineQueryResultVideo,
)

from services import rule34_service, danbooru_service, safebooru_service, konachan_service

sys.path.append("..")
router = Router()

RANDOM_URLS = {
    "r34": "https://rule34.xxx/index.php?page=post&s=random",
    "danbooru": "https://danbooru.donmai.us/posts/random",
    "safebooru": "https://safebooru.org/index.php?page=post&s=random",
    "kona": "https://konachan.net/post.json?limit=1&tags=order%3Arandom",
}


def _process_item(item_data: dict, service_name: str):
    file_url = item_data.get("file_url")
    if not file_url:
        return None

    post_id = item_data.get("id")
    
    source_map = {
        "r34": f"https://rule34.xxx/index.php?page=post&s=view&id={post_id}",
        "danbooru": f"https://danbooru.donmai.us/posts/{post_id}",
        "safebooru": f"https://safebooru.org/index.php?page=post&s=view&id={post_id}",
    }
    uid_map = {
        "r34": f"random_r34_{item_data.get('hash')}",
        "danbooru": f"random_danbooru_{item_data.get('md5')}",
        "safebooru": f"random_safebooru_{item_data.get('hash')}",
    }

    thumb = None
    if service_name == 'danbooru':
        thumb = item_data.get('large_file_url') or item_data.get('preview_file_url')
    else:
        thumb = item_data.get('sample_url') or item_data.get('preview_url')
    
    if thumb == file_url:
        thumb = item_data.get('preview_file_url') or item_data.get('preview_url')

    if not thumb:
        return None

    source_url = source_map[service_name]
    caption = hlink('Source', source_url)
    uid = uid_map[service_name]


    final_ext = item_data.get('file_ext', file_url.split('.')[-1]).lower()

    if final_ext == "gif":
        return InlineQueryResultGif(id=uid, gif_url=file_url, thumbnail_url=thumb, parse_mode=ParseMode.HTML, caption=caption)
    
    elif final_ext in ["mp4", "webm"]:
        width, height = item_data.get("width"), item_data.get("height")
        duration = int(float(item_data.get("duration", 0)))
        return InlineQueryResultVideo(id=uid, video_url=file_url, mime_type=f"video/{final_ext}", thumbnail_url=thumb, title=f"Random from {service_name.capitalize()}", parse_mode=ParseMode.HTML, caption=caption, video_width=width, video_height=height, video_duration=duration)
    
    elif final_ext in ["jpg", "jpeg", "png"]:
        return InlineQueryResultPhoto(id=uid, photo_url=file_url, thumbnail_url=thumb, parse_mode=ParseMode.HTML, caption=caption)
    
    else:
        return None


async def get_post_id_from_redirect(session, url: str, service_name: str) -> str | None:
    try:
        async with session.get(url, allow_redirects=True, timeout=10) as response:
            if response.status == 200:
                final_url = str(response.url)
                match = re.search(r"id=(\d+)", final_url) if service_name != 'danbooru' else re.search(r"/posts/(\d+)", final_url)
                if match:
                    post_id = match.group(1)
                    return post_id
            else:
                print(f" Received status code: {response.status}")
    except Exception as e:
        print(f" An exception occurred: {e}")
    return None


@router.inline_query(F.query.strip().lower() == "random")
async def send_random_media(inline_query: InlineQuery):
    chosen_service = random.choice(list(RANDOM_URLS.keys()))
    random_url = RANDOM_URLS[chosen_service]

    try:
        async with aiohttp.ClientSession() as session:
            if chosen_service == "kona":
                async with session.get(random_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if not data:
                            await inline_query.answer([], cache_time=0, is_personal=True)
                            return
                        post_id = data[0].get("id")
                    else:
                        post_id = None
            else:
                post_id = await get_post_id_from_redirect(session, random_url, chosen_service)

        if not post_id:
            await inline_query.answer([], cache_time=0, is_personal=True)
            return

        service_map = {
            "r34": rule34_service.get_post_list,
            "danbooru": danbooru_service.get_post_list,
            "safebooru": safebooru_service.get_post_list,
            "kona": lambda **kwargs: konachan_service.get_post_list(**kwargs, nsfw=False),
        }

        response_data = await service_map[chosen_service](tags=f"id:{post_id}", limit=1)

        if not response_data:
            await inline_query.answer([], cache_time=0, is_personal=True)
            return

        processed_item = _process_item(response_data[0], chosen_service)
        if not processed_item:
            await inline_query.answer([], cache_time=0, is_personal=True)
            return

        await inline_query.answer([processed_item], cache_time=0, is_personal=True)

    except Exception as e:
        print(f"[FATAL] Error in send_random_media: {e}")
        await inline_query.answer([], cache_time=0, is_personal=True)