Unalix is a simple code library written in Python. It implements the same regex rule processing mechanism used by the [ClearURLs](https://github.com/ClearURLs/Addon) addon.

#### Features

- **Sync and Async**: Unalix supports both sync and async calls, fit for all usage needs.
- **Type-hinted**: All methods are type-hinted, enabling excellent editor support.
- **Simple**: No extra dependence is required to use this library.

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

with_tracking_field = 'https://deezer.com/track/891177062?utm_source=deezer'
without_tracking_field = clear_url(with_tracking_field)

print(without_tracking_field)
```

Unshortening a shortened URL:

```python
from unalix import unshort_url

shortened_url = 'https://bitly.is/Pricing-Pop-Up'
unshortened_url = unshort_url(shortened_url)

print(unshortened_url)
```

Output from both examples:

```bash
https://deezer.com/track/891177062
https://bitly.com/pages/pricing
```

_**Note**: Unalix also has a command line tool called `clear_url`._

#### Limitations

- Getting direct links from URL shorteners
  - Unalix only follows the URLs/paths provided by the `Location` header (see [RFC 7231, section 7.1.2: Location](https://tools.ietf.org/html/rfc7231#section-7.1.2)). It means that Unalix cannot obtain direct links from URL shorteners that require user interaction (e.g clicking a button or resolving CAPTCHA) to redirect or that uses JavaScript code to redirect.

#### Contributing

If you have discovered a bug in this library and know how to fix it, fork this repository and open a Pull Request. Otherwise, open a issue to report it.

If you found a URL that was not fully cleaned by Unalix (e.g some tracking fields still remains), report it here or in the [ClearURLs addon repository](https://github.com/ClearURLs/Addon/issues). We use the list of regex rules maintained by the ClearURLs maintainers, but we also have our [own list](https://github.com/AmanoTeam/Unalix/blob/master/unalix/package_data/unalix-data.min.json).

#### Third party software

Unalix includes some third party software. See them below:

- **ClearURLs**
  - Author: Kevin Röbert
  - Repository: [ClearURLs/Addon](https://github.com/ClearURLs/Addon)
  - License: [GNU Lesser General Public License v3.0](https://gitlab.com/ClearURLs/Addon/blob/master/LICENSE)

- **Pyrogram**
  - Author: Dan
  - Repository: [pyrogram/pyrogram](https://github.com/pyrogram/pyrogram)
  - License: [GNU Lesser General Public License v3.0](https://github.com/pyrogram/pyrogram/blob/master/COPYING)

- **python-requests**
  - Author: Kenneth Reitz
  - Repository: [psf/requests](https://github.com/psf/requests)
  - License: [Apache v2.0](https://github.com/psf/requests/blob/master/LICENSE)
