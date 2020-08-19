import json
import os

json_files_dir = os.path.join(
	os.path.dirname(__file__), 'json_files', ''
)

# https://www.whatismybrowser.com/guides/the-latest-user-agent/
user_agents = open(os.path.join(json_files_dir, 'user_agents.json')).read()
user_agents = json.loads(user_agents)

# https://github.com/soimort/translate-shell/wiki/Languages
languages = open(os.path.join(json_files_dir, 'language_codes.json')).read()
languages = json.loads(languages)

rules = []

# https://gitlab.com/KevinRoebert/ClearUrls/-/blob/master/data/data.min.json
# https://github.com/AmanoTeam/Unalix/blob/master/unalix/json_files/custom-data.min.json
for filename in ['data.min.json',  'custom-data.min.json']:
	rules += [json.loads(open(os.path.join(json_files_dir, filename), 'r').read())]

# format: (r'pattern', r'replacement')
replacements = [
	(r'(%26)+', r'%26'),
	(r'&+', r'&'),
	(r'(%3f|%3F)+', r'%3f'),
	(r'(%3f|%3F|\?|%23|&)+$', r''),
	(r'\?&',  r'?'),
	(r'(%3f%26|%3F%26)', r'%3f')
]

__title__ = 'Unalix'
__description__ = 'A simple module that removes tracking fields from URLs.'
__version__ = '0.5'

__all__ = [
	'__title__',
	'__description__',
	'__version__',
	'http_clients',
	'patches',
	'settings',
	'utils',
	'clear_url'
]