import os
import json

package_data = os.path.join(
	os.path.dirname(__file__), 'package_data', ''
)

# https://www.whatismybrowser.com/guides/the-latest-user-agent/
with open(os.path.join(package_data, 'user_agents.json')) as file_object:
	file_content = file_object.read()
	user_agents = json.loads(file_content)

# https://gitlab.com/KevinRoebert/ClearUrls/-/blob/master/data/data.min.json
# https://github.com/AmanoTeam/Unalix/blob/master/unalix/json_files/custom-data.min.json
rules = []

for filename in ['data.min.json',  'custom-data.min.json']:
	with open(os.path.join(package_data, filename), 'r') as file_object:
		file_content = file_object.read()
	dict = json.loads(file_content)
	rules += [dict]

del dict
del file_content
del file_object
