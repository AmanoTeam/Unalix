import json
import os
import pathlib
import re
import setuptools


def get_version():
	"""
	Return package version as listed in `__version__`.
	"""
	
	with open(file=os.path.join(module_path, "unalix", "__version__.py"), mode="r") as file:
		content = file.read()
	
	result = re.search('__version__ = "([0-9\.]+)"', content)
	
	return result.group(1)


def get_long_description():
	"""
	Return the README.
	"""
	
	with open(file="README.md", mode="r") as file:
		content = file.read()
	
	return content


def get_packages():
	"""
	Return root package and all sub-packages.
	"""
	
	return [
		str(path.parent) for path in pathlib.Path("unalix").glob("**/__init__.py")
	]

module_path = pathlib.Path(__file__).parent

version = get_version()
long_description = get_long_description()

packages = get_packages()

package_data = {
	"unalix": [
		"package_data/ca/ca-bundle.crt",
		"package_data/other/redirects_from_body.json",
		"package_data/policies/cookies_allow.json",
		"package_data/rulesets/data.min.json",
		"package_data/rulesets/unalix.json"
	]
}

classifiers = [
	"License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
	"Operating System :: Unix"
	"Topic :: Internet",
	"Topic :: Security",
	"Development Status :: 5 - Production/Stable",
	"Intended Audience :: Developers",
	"Programming Language :: Python :: 3.7",
	"Programming Language :: Python :: 3.8",
	"Programming Language :: Python :: 3.9"
]

bad_keys = (
	"ClearURLsTest",
	"ClearURLsTestBlock",
	"ClearURLsTest2",
	"ClearURLsTestBlock2"
)

for filename in package_data["unalix"]:
	
	if not filename.endswith(".json"):
		continue
	
	with open(os.path.join(module_path, "unalix", filename), mode="r+") as file:
		content = file.read()
		
		ruleset = json.loads(content)
		
		try:
			for key in bad_keys:
				del ruleset["providers"][key]
		except (KeyError, TypeError):
			pass
		
		file.seek(0)
		file.write(json.dumps(ruleset))
		file.truncate()

setuptools.setup(
	name="Unalix",
	version=version,
	author="SnwMds",
	author_email="snwmds@tutanota.com",
	description="A simple module that removes tracking fields from URLs and unshort shortened URLs.",
	license="LGPL-3.0",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/AmanoTeam/Unalix",
	packages=packages,
	include_package_data=True,
	package_data=package_data,
	classifiers=classifiers,
	python_requires=">=3.7",
)
