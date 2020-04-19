import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unalix",
    version="0.1",
    author="Amano Team",
    author_email="contact@amanoteam.com",
    description="A simple module that removes tracking fields from URLs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SnwMds/Unalix",
    install_requires=[ 'requests' ],
    packages=[ 'unalix' ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Internet",
    ],
    python_requires='>=3.6',
)

