import json
import http.client
import urllib.parse

ca_url = "https://curl.se/ca/cacert.pem"
ca_path = "unalix/package_data/ca/ca-bundle.crt"

url = urllib.parse.urlparse(ca_url)

connection = http.client.HTTPSConnection(
	host = url.netloc,
	port = url.port
)

print(f"Fetching data from {ca_url}...")

connection.request(
	method = "GET",
	url = url.path
)
response = connection.getresponse()

content = response.read()

with open(file = ca_path, mode = "wb") as file:
    file.write(content)
