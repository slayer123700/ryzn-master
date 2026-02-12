import aiohttp
import io

async def make_carbon(text: str) -> io.BytesIO:
    """
    Generates a carbon image from given text using Carbonara API.
    Returns an in-memory BytesIO object ready to send.
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://carbonara.vercel.app/api/cook?code={text}"
        async with session.get(url) as resp:
            data = await resp.read()
            carbon = io.BytesIO(data)
            carbon.name = "carbon.png"
            return carbon