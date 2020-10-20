import json
from urllib.parse import urlparse

from unalix._http import create_connection, get_encoded_content
from unalix._config import headers, timeout

rules_url = "https://kevinroebert.gitlab.io/ClearUrls/data/data.min.json"
rules_path = "unalix/package_data/data.min.json"

scheme, netloc, path, params, query, fragment = urlparse(rules_url)
connection = create_connection(scheme, netloc)

print(f"Fetching data from {rules_url}...")

connection.request("GET", path, headers=headers)
response = connection.getresponse()

rules = json.loads(get_encoded_content(response))

with open(rules_path, mode="w+", encoding="utf-8") as file_object:
    file_object.write(json.dumps(rules, indent=4))