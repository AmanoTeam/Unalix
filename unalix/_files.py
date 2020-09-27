import os
import json

from unalix._settings import (
	package_data,
	json_rules
)

# https://www.whatismybrowser.com/guides/the-latest-user-agent/
with open(os.path.join(package_data, 'user_agents.json')) as file_object:
	file_content = file_object.read()
	user_agents = json.loads(file_content)

rules = []

for filename in json_rules:
	with open(os.path.join(package_data, filename), 'r') as file_object:
		file_content = file_object.read()
	dict = json.loads(file_content)
	rules += [dict]

del dict
del file_content
del file_object
