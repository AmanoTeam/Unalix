import json
import http.client

from unalix.config.http import (
	HTTP_HEADERS,
	HTTP_TIMEOUT
)
from unalix.core.ssl_context import SSL_CONTEXT
from unalix.types import URL

ca_url = "https://curl.se/ca/cacert.pem"
ca_path = "unalix/package_data/ca/ca-bundle.crt"

url = URL(ca_url)

connection = http.client.HTTPSConnection(
	host=url.netloc,
	port=url.port,
	timeout=HTTP_TIMEOUT,
	context=SSL_CONTEXT
)

print(f"Fetching data from {ca_url}...")

connection.request(
	method="GET",
	url=url.path,
	headers=HTTP_HEADERS
)
response = connection.getresponse()

content = response.read()

with open(ca_path, mode="wb") as file:
    file.write(content)
