import httpx
import asyncio

async def test():
    try:
        # Disable proxy
        async with httpx.AsyncClient(trust_env=False) as client:
            r = await client.get('http://127.0.0.1:8005/health')
            print(f"Status: {r.status_code}")
            print(f"Text: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
