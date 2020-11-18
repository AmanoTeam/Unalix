import json
from urllib.parse import urlparse

from unalix._http import create_connection, get_encoded_content
from unalix._config import default_headers

rules_url = "https://rules1.clearurls.xyz/data/data.minify.json"
rules_path = "unalix/package_data/data.min.json"

scheme, netloc, path, params, query, fragment = urlparse(rules_url)
connection = create_connection(scheme, netloc)

print(f"Fetching data from {rules_url}...")

connection.request("GET", path, headers=default_headers)
response = connection.getresponse()

content = get_encoded_content(response))
rules = json.loads(content)

with open(rules_path, mode="w", encoding="utf-8") as file:
    file.write(json.dumps(rules, indent=4))
