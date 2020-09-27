import json
import os

# format: (r'pattern', r'replacement')
replacements = [
	(r'(%26)+', r'%26'),
	(r'&+', r'&'),
	(r'(%3f|%3F)+', r'%3f'),
	(r'(%3f|%3F|\?|%23|&)+$', r''),
	(r'\?&',  r'?'),
	(r'(%3f%26|%3F%26)', r'%3f')
]
