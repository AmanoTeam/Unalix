from setuptools import setup

with open('README.md', 'r') as file_object:
    long_description = file_object.read()

package_data = {
    'unalix': [
        'package_data/custom-data.min.json',
        'package_data/data.min.json',
        'package_data/language_codes.json',
        'package_data/user_agents.json'
    ]
}

classifiers = [
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Operating System :: Unix',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Security',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
]

requirements = [
    'httpx[http2]==0.15.1'
]

setup(
    name='Unalix',
    version='0.5',
    author='Amano Team',
    author_email='contact@amanoteam.com',
    description='A simple module that removes tracking fields from URLs and unshort shortened URLs.',
    license='LGPL-3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AmanoTeam/Unalix',
    install_requires=requirements,
    packages=['unalix'],
    include_package_data=True,
    package_data=package_data,
    classifiers=classifiers,
    python_requires='>=3.6',
)
