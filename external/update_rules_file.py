import json
import http.client
import urllib.parse

rules_url = "https://rules1.clearurls.xyz/data/data.minify.json"
rules_path = "unalix/package_data/rulesets/data.min.json"

url = urllib.parse.urlparse(rules_url)

connection = http.client.HTTPSConnection(
	host = url.netloc,
	port = url.port
)

print(f"Fetching data from {rules_url}...")

connection.request(
	method = "GET",
	url = url.path
)
response = connection.getresponse()

content = content = response.read()

rules = json.loads(content)

with open(file = rules_path, mode = "w") as file:
    file.write(json.dumps(rules, indent = 4))
