import json
import http.client

import unalix

ca_url = "https://curl.se/ca/cacert.pem"
ca_path = "unalix/package_data/ca/ca-bundle.crt"

url = unalix.types.URL(ca_url)

connection = http.client.HTTPSConnection(
	host=url.netloc,
	port=url.port,
	timeout=unalix.config.HTTP_TIMEOUT,
	context=unalix.SSL_CONTEXT_VERIFIED
)

print(f"Fetching data from {ca_url}...")

connection.request(
	method="GET",
	url=url.path,
	headers=unalix.config.HTTP_HEADERS
)
response = connection.getresponse()

content = response.read()

with open(ca_path, mode="wb") as file:
    file.write(content)
