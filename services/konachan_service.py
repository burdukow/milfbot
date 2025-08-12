from aiohttp import ClientSession
from services.config import settings

async def get_post_list(tags="", limit=50, page=1):
    base_url = settings.konachan_url
    async with ClientSession() as session:
        url = f"{base_url}?limit={limit}&page={page}"
        if tags:
            url += f"&tags={tags} -ai_generated -ai -ai_assisted"

        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return []
