from httpx import Client

headers = { 
	'Accept': 'text/html',
	'Accept-Encoding': 'gzip, deflate',
	'Cache-Control' :'no-cache, no-store'
}

client = Client(
	headers=headers
)
