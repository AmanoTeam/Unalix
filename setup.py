import json
import os

from setuptools import setup

with open("README.md", mode="r", encoding="utf-8") as file_object:
    content = file_object.read()

package_data = {
    "unalix": [
        "package_data/unalix-data.min.json",
        "package_data/data.min.json",
        "package_data/arguments.json",
        "package_data/ca-bundle.crt",
        "package_data/body_redirects.json",
        "package_data/cookies_required.json"
    ]
}

classifiers = [
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Operating System :: Unix",
    "Operating System :: Android",
    "Topic :: Internet",
    "Topic :: Security",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9"
]

module_path = os.path.dirname(__file__)

bad_json_keys = [
    "ClearURLsTest",
    "ClearURLsTestBlock",
    "ClearURLsTest2",
    "ClearURLsTestBlock2"
]

for filename in package_data["unalix"]:
    if not filename.endswith(".json"):
        continue
    with open(f"{module_path}/unalix/{filename}", mode="r+", encoding="utf-8") as file_object:
        json_rules = json.loads(file_object.read())
        try:
            for bad_key in bad_json_keys:
                del json_rules["providers"][bad_key]
        except (KeyError, TypeError):
            pass
        file_object.seek(0)
        file_object.write(json.dumps(json_rules))
        file_object.truncate()

setup(
    name="Unalix",
    version="0.6",
    author="SnwMds",
    author_email="snwmds@amanoteam.com",
    description="A simple module that removes tracking fields from URLs and unshort shortened URLs.",
    license="LGPL-3.0",
    long_description=content,
    long_description_content_type="text/markdown",
    url="https://github.com/AmanoTeam/Unalix",
    packages=["unalix"],
    include_package_data=True,
    package_data=package_data,
    entry_points={"console_scripts": ["unalix = unalix._command_line:main"]},
    classifiers=classifiers,
    python_requires=">=3.6",
)
