from httpx import Client

headers = { 'Cache-Control' :'no-cache' }

client = Client(http2=True, headers=headers)
