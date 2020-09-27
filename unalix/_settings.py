import os

# Path to directory containing the package data (json files)
package_data = os.path.join(
	os.path.dirname(__file__), 'package_data', ''
)

# Json files containing regex patterns
json_rules = [
	'data.min.json', 
	'custom-data.min.json'
]

# format: (r'pattern', r'replacement')
replacements = [
	(r'(%26)+', r'%26'),
	(r'&+', r'&'),
	(r'(%3f|%3F)+', r'%3f'),
	(r'(%3f|%3F|\?|%23|&)+$', r''),
	(r'\?&',  r'?'),
	(r'(%3f%26|%3F%26)', r'%3f')
]
