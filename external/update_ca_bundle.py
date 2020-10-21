import json
from urllib.parse import urlparse

from unalix._http import create_connection, get_encoded_content
from unalix._config import headers, timeout

ca_url = "https://curl.haxx.se/ca/cacert.pem"
ca_path = "unalix/package_data/ca-bundle.crt"

scheme, netloc, path, params, query, fragment = urlparse(ca_url)
connection = create_connection(scheme, netloc)

print(f"Fetching data from {ca_url}...")

connection.request("GET", path, headers=headers) # type: ignore
response = connection.getresponse() # type: ignore

content = get_encoded_content(response)

with open(ca_path, mode="w+", encoding="utf-8") as file_object:
    file_object.write(content) # type: ignore