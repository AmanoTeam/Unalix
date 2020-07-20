### What it does?

In addition to removing tracking fields from URLs, Unalix also try to gets the direct link from shortened URLs.

Unalix also transform YouTube, Twitter and Instagram links into Invidious, Nitter and Bibliogram links.

### Installation

```
pip3 install --upgrade 'unalix'
```
or
```
pip3 install --upgrade 'git+https://github.com/SnwMds/Unalix'
```

The git repository will always have the most recent changes, so it is recommended that you install/update the module through it.

### Usage:

Let's see some examples:

**On a Python3 console:**

```python
>>> from unalix import clear_url
>>> 
>>> clear_url('http://example.com/?utm_source=amp&__twitter_impression=true')
'http://example.com/index.html'
>>> 
>>> clear_url('http://goo.gl/ko4LWp')
'https://forum.xda-developers.com/android/apps-games/app-youtube-vanced-edition-t3758757'
>>> 
>>> clear_url('https://youtu.be/o5DnSWi06b8')
'https://invidio.us/watch?v=o5DnSWi06b8'
>>> 
>>> clear_url('https://twitter.com/funimation')
'https://nitter.net/funimation'
>>> 
>>> clear_url('https://www.instagram.com/p/B89TWTdlEXf/')
'https://bibliogram.pussthecat.org/p/B89TWTdlEXf/'
>>>
```

**On a bash terminal:**

```bash
$ unalix --url 'http://example.com/?utm_source=amp&__twitter_impression=true'
http://example.com/index.html
$
$ unalix --url 'http://goo.gl/ko4LWp'
https://forum.xda-developers.com/android/apps-games/app-youtube-vanced-edition-t3758757
$
$ unalix --url  'https://twitter.com/funimation'
https://nitter.net/funimation
$
```

### Limitations

Unalix has some limitations related to link processing, see them below:

#### Getting direct links from URL shorteners

Unalix only follows the URLs/paths provided by the `Location` header (see [RFC 7231, section 7.1.2: Location](https://tools.ietf.org/html/rfc7231#section-7.1.2)). It means that Unalix cannot obtain direct links from URL shorteners that require user interaction (e.g clicking a button or resolving CAPTCHA) to redirect or that uses JavaScript code to redirect.

### Contact

Want to say something? Need some help? [Open a issue](https://github.com/SnwMds/Unalix/issues) or [send a email](https://spamty.eu/show.php?version=v6&email=26&key=d7967f0e625c5f19c9c655b8).

### License

Unalix in licensed under the [GNU Lesser General Public License v3.0](https://github.com/AmanoTeam/Unalix/blob/master/LICENSE).

### Third party software

Unalix includes some third party software. See them below:

- **ClearURLs**
  - Author: Kevin Röbert ([KevinRoebert](https://gitlab.com/KevinRoebert))
  - Repository: [KevinRoebert/ClearUrls](https://gitlab.com/KevinRoebert/ClearUrls)
  - License: [GNU Lesser General Public License v3.0](https://gitlab.com/KevinRoebert/ClearUrls/blob/master/LICENSE)
