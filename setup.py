from setuptools import setup

long_description = open('README.md', 'r').read()

package_data = {
    'unalix': [
        'json_files/custom-data.min.json',
        'json_files/data.min.json',
        'json_files/language_codes.json',
        'json_files/user_agents.json'
    ]
}

setup(
    name='Unalix',
    version='0.5',
    author='Amano Team',
    author_email='contact@amanoteam.com',
    description='A simple module that removes tracking fields from URLs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AmanoTeam/Unalix',
    install_requires=['httpx[http2]==0.14.1', 'rfc3986==1.4.0', 'idna==2.10'],
    packages=['unalix'],
    include_package_data=True,
    package_data=package_data,
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: Unix',
        'Topic :: Internet',
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    python_requires='>=3.6',
)
