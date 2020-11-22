Unalix is a simple code library written in Python. It implements the same regex rule processing mechanism used by the [ClearURLs](https://github.com/ClearURLs/Addon) addon.

#### Installation

Install using `pip`:

```bash
pip3 install --force-reinstall \
    --disable-pip-version-check \
    --upgrade 'unalix'
```

_**Note**: Unalix requires Python 3.6 or higher._

#### Usage:

Removing tracking fields:

```python
from unalix import clear_url

url = 'https://deezer.com/track/891177062?utm_source=deezer'
result = clear_url(url)

print(result)
```

Unshortening a shortened URL:

```python
from unalix import unshort_url

url = 'https://bitly.is/Pricing-Pop-Up'
result = unshort_url(url)

print(result)
```

Output from both examples:

```bash
https://deezer.com/track/891177062
https://bitly.com/pages/pricing
```

#### Contributing

If you have discovered a bug in this library and know how to fix it, fork this repository and open a Pull Request.

If you found a URL that was not fully cleaned by Unalix (e.g. some tracking fields still remains), report them here or in the [ClearURLs addon repository](https://gitlab.com/anti-tracking/ClearURLs/rules/-/issues/new). We use the list of regex rules maintained by the ClearURLs maintainers, but we also have our [own list](./unalix/package_data/unalix-data.min.json).

#### Third party software

Unalix includes some third party software. See them below:

- **ClearURLs**
  - Author: Kevin Röbert
  - Repository: [ClearURLs/Rules](https://github.com/ClearURLs/Rules)
  - License: [GNU Lesser General Public License v3.0](https://gitlab.com/ClearURLs/Rules/blob/master/LICENSE)

- **python-requests**
  - Author: Kenneth Reitz
  - Repository: [psf/requests](https://github.com/psf/requests)
  - License: [Apache v2.0](https://github.com/psf/requests/blob/master/LICENSE)
