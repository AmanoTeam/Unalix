import ipaddress
from urllib.parse import quote, urlparse, urlunparse

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L566
# The unreserved URI characters (RFC 3986)
UNRESERVED_SET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789-._~")

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L570
def unquote_unreserved(uri):
    """Un-escape any percent-escape sequences in a URI that are unreserved
    characters. This leaves all reserved, illegal and non-ASCII bytes encoded.
    """
    parts = uri.split("%")
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            c = chr(int(h, 16))
            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = "%" + parts[i]
        else:
            parts[i] = "%" + parts[i]
    return "".join(parts)

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L594
def requote_uri(uri):
    """Re-quote the given URI.

    This function passes the given URI through an unquote/quote cycle to
    ensure that it is fully and consistently quoted.
    """
    safe_with_percent = "!#$%&'()*+,/:;=?@[]~"
    safe_without_percent = "!#$&'()*+,/:;=?@[]~"
    try:
        # Unquote only the unreserved characters
        # Then quote only illegal characters (do not quote reserved,
        # unreserved, or '%')
        return quote(unquote_unreserved(uri), safe=safe_with_percent)
    except ValueError:
        # We couldn't unquote the given URI, so let"s try quoting it, but
        # there may be unquoted "%"s in the URI. We need to make sure they're
        # properly quoted so they do not cause issues elsewhere.
        return quote(uri, safe=safe_without_percent)

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L894
def prepend_scheme_if_needed(url, new_scheme):
    """Given a URL that may or may not have a scheme, prepend the given scheme.
    Does not replace a present scheme with the one provided as an argument.
    """
    scheme, netloc, path, params, query, fragment = urlparse(url, new_scheme)

    # urlparse is a finicky beast, and sometimes decides that there isn't a
    # netloc present. Assume that it's being over-cautious, and switch netloc
    # and path if urlparse decided there was no netloc.
    if not netloc:
        netloc, path = path, netloc

    return urlunparse((
        scheme, netloc, path, params, query, fragment
    ))

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L953
def urldefragauth(url):
    """Given a url remove the fragment and the authentication part."""
    scheme, netloc, path, params, query, fragment = urlparse(url)

    # see func:`prepend_scheme_if_needed`
    if not netloc:
        netloc, path = path, netloc

    netloc = netloc.rsplit("@", 1)[-1]

    return urlunparse((scheme, netloc, path, params, query, ''))

def is_private(netloc):
    """This function checks if the URL's netloc belongs to a local/private network.

    Usage:
      >>> from unalix._utils import is_private
      >>> is_private("0.0.0.0")
      True
    """

    local_domains = [
        "localhost",
        "localhost.localdomain",
        "ip6-localhost",
        "ip6-loopback"
    ]

    try:
        address = ipaddress.ip_address(netloc)
    except ValueError:
        return (netloc in local_domains)
    else:
        return address.is_private

def strip_parameters(value):
    """This function is used strip parameters from header values.

    Usage:
      >>> from unalix._utils import strip_parameters
      >>> strip_parameters('text/html; charset="utf-8"')
      'text/html'
    """
    return value.rsplit(";", 1)[0].rstrip(" ")

def remove_invalid_parameters(url):
    """This function is used to remove invalid parameters from URLs.

    Usage:
      >>> from unalix._utils import remove_invalid_parameters
      >>> remove_invalid_parameters("http://example.com/?p1&p2=&p3=p=&&p4=v")
      'http://example.com/?p4=v'
    """
    scheme, netloc, path, params, query, fragment = urlparse(url)

    if not query:
        return urlunparse((
            scheme, netloc, path, params, query, fragment
        ))

    new_query_list, new_query_dict = [], {}

    for param in query.split("&"):
        try:
            key, value = param.split("=")
        except ValueError:
            continue
        else:
            if value:
                new_query_dict.update(
                    {
                        key: value
                    }
                )

    for key, value in new_query_dict.items():
        new_query_list += [
            f"{key}={value}"
        ]

    return urlunparse((
        scheme, netloc, path, params, "&".join(new_query_list), fragment
    ))
