Unalix is a library written in Python, it follows the same specification used by the [ClearURLs](https://github.com/ClearURLs/Addon) addon for removing tracking fields from URLs.

#### Installation

Install using `pip`:

```bash
python3 -m pip install --force-reinstall \
    --disable-pip-version-check \
    --upgrade \
    'unalix'
```

The version from git might be broken sometimes, but you can also install from it:

```bash
python3 -m pip install --force-reinstall \
    --disable-pip-version-check \
    --upgrade \
    'https://codeload.github.com/AmanoTeam/Unalix/tar.gz/refs/heads/master'
```

_**Note**: Unalix requires Python 3.6 or higher._

#### Usage:

Removing tracking fields:

```python
import unalix

url: str = "https://deezer.com/track/891177062?utm_source=deezer"
result: str = unalix.clear_url(url=url)

print(result)
```

Unshort shortened URL:

```python
import unalix

url: str = "https://bitly.is/Pricing-Pop-Up"
result: str = unalix.unshort_url(url=url)

print(result)
```

Output from both examples:

```
https://deezer.com/track/891177062
https://bitly.com/pages/pricing
```

_**Tip**: `unshort_url()` will strip tracking fields from any URL before following a redirect, so you don't need to manually call `clear_url()` for it's return value._

#### Contributing

If you have discovered a bug in this library and know how to fix it, fork this repository and open a Pull Request.

#### Third party software

Unalix includes some third party software in its codebase. See them below:

- **ClearURLs**
  - Author: Kevin Röbert
  - Repository: [ClearURLs/Rules](https://github.com/ClearURLs/Rules)
  - License: [GNU Lesser General Public License v3.0](https://gitlab.com/ClearURLs/Rules/blob/master/LICENSE)

- **Requests**
  - Author: Kenneth Reitz
  - Repository: [psf/requests](https://github.com/psf/requests)
  - License: [Apache v2.0](https://github.com/psf/requests/blob/master/LICENSE)

- **Pyrogram**
  - Author: Dan
  - Repository: [pyrogram/pyrogram](https://github.com/pyrogram/pyrogram)
  - License: [LGPL-3.0](https://github.com/pyrogram/pyrogram/blob/master/COPYING)
