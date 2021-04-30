import json
import http.client

import unalix

rules_url = "https://rules1.clearurls.xyz/data/data.minify.json"
rules_path = "unalix/package_data/rulesets/data.min.json"

url = unalix.types.URL(rules_url)

connection = http.client.HTTPSConnection(
	host=url.netloc,
	port=url.port,
	timeout=unalix.config.HTTP_TIMEOUT,
	context=unalix.SSL_CONTEXT_VERIFIED
)

print(f"Fetching data from {rules_url}...")

connection.request(
	method="GET",
	url=url.path,
	headers=unalix.config.HTTP_HEADERS
)
response = connection.getresponse()

content = content = response.read()

rules = json.loads(content)

with open(file=rules_path, mode="w", encoding="utf-8") as file:
    file.write(json.dumps(rules, indent=4))
