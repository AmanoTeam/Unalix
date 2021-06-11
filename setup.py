import os
import pathlib
import re

import setuptools


def get_version():
    """
    Return package version as listed in `__version__`.
    """

    with open(file=os.path.join(pathlib.Path(__file__).parent, "unalix", "__version__.py"), mode="r") as file:
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


version = get_version()
long_description = get_long_description()

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
    "Operating System :: Unix",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Topic :: Internet",
    "Topic :: Security",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: Implementation :: PyPy"
]

setuptools.setup(
    name="Unalix",
    version=version,
    author="SnwMds",
    author_email="snwmds@tutanota.com",
    description="Small, dependency-free, fast Python package for removing tracking fields from URLs.",
    license="LGPL-3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmanoTeam/Unalix",
    project_urls={
        "Bug Tracker": "https://github.com/AmanoTeam/Unalix/issues",
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data=package_data,
    classifiers=classifiers,
    python_requires=">=3.6",
)
