import json
import http.client

from unalix.config.http import (
	HTTP_HEADERS,
	HTTP_TIMEOUT
)
from unalix.core.ssl_context import SSL_CONTEXT
from unalix.types import URL

rules_url = "https://rules1.clearurls.xyz/data/data.minify.json"
rules_path = "unalix/package_data/rulesets/data.min.json"

url = URL(rules_url)

connection = http.client.HTTPSConnection(
	host=url.netloc,
	port=url.port,
	timeout=HTTP_TIMEOUT,
	context=SSL_CONTEXT
)

print(f"Fetching data from {rules_url}...")

connection.request(
	method="GET",
	url=url.path,
	headers=HTTP_HEADERS
)
response = connection.getresponse()

content = content = response.read()

rules = json.loads(content)

with open(file=rules_path, mode="w", encoding="utf-8") as file:
    file.write(json.dumps(rules, indent=4))
