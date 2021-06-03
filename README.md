Unalix is a library written in Python, it follows the same specification used by the [ClearURLs](https://github.com/ClearURLs/Addon) addon for removing tracking fields from URLs.

#### Installation

Install using `pip`:

```bash
python3 -m pip install --force-reinstall \
    --disable-pip-version-check \
    --upgrade 'unalix'
```

The version from git might be broken sometimes, but you can also install from it:

```bash
python3 -m pip install --force-reinstall \
    --disable-pip-version-check \
    --upgrade 'git+https://github.com/AmanoTeam/Unalix'
```

_**Note**: Unalix requires Python 3.6 or higher._

#### Usage:

Removing tracking fields:

```python
import unalix

url = "https://deezer.com/track/891177062?utm_source=deezer"
result = unalix.clear_url(url)

print(result)
```

Unshort shortened URL:

```python
import unalix

url = "https://bitly.is/Pricing-Pop-Up"
result = unalix.unshort_url(url)

print(result)
```

Output from both examples:

```bash
https://deezer.com/track/891177062
https://bitly.com/pages/pricing
```

_**Tip**: `unshort_url()` will strip tracking fields from any URL before following a redirect, so you don't need to manually call `clear_url()` for it._

#### Contributing

If you have discovered a bug in this library and know how to fix it, fork this repository and open a Pull Request.

If you found a URL that was not fully cleaned by Unalix (e.g. some tracking fields still remains), report them here or in the [ClearURLs rules repository](https://gitlab.com/anti-tracking/ClearURLs/rules/-/issues). We use the list of regex rules maintained by the ClearURLs maintainers, but we also have our [own list](./unalix/package_data/rulesets/unalix.json).

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
