from httpx import Client

headers = { 
	'Accept': 'text/html',
	'Connection': 'close',
	'Accept-Encoding': 'gzip, deflate'
}

client = Client(
	http2=True,
	headers=headers
)
