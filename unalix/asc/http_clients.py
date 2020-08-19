from httpx import AsyncClient

headers = { 'Cache-Control' :'no-cache' }

client = AsyncClient(http2=True, headers=headers)
