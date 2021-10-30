import string
import urllib.parse
import typing

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L566
# The unreserved URI characters (RFC 3986)
UNRESERVED_SET = frozenset(
    string.ascii_uppercase + string.ascii_lowercase + string.digits + "-._~"
)

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
        return urllib.parse.quote(unquote_unreserved(uri), safe=safe_with_percent)
    except ValueError:
        # We couldn't unquote the given URI, so let"s try quoting it, but
        # there may be unquoted "%"s in the URI. We need to make sure they're
        # properly quoted so they do not cause issues elsewhere.
        return urllib.parse.quote(uri, safe=safe_without_percent)


# https://github.com/psf/requests/blob/v2.25.1/requests/utils.py#L461
def _parse_content_type_header(header):
    """Returns content type and parameters from given header

    :param header: string
    :return: tuple containing content type and dictionary of
         parameters
    """

    tokens = header.split(';')
    content_type, params = tokens[0].strip(), tokens[1:]
    params_dict = {}
    items_to_strip = "\"' "

    for param in params:
        param = param.strip()
        if param:
            key, value = param, True
            index_of_equals = param.find("=")
            if index_of_equals != -1:
                key = param[:index_of_equals].strip(items_to_strip)
                value = param[index_of_equals + 1:].strip(items_to_strip)
            params_dict[key.lower()] = value
    return content_type, params_dict

# https://github.com/psf/requests/blob/v2.25.1/requests/utils.py#L486
def get_encoding_from_headers(headers):
    """Returns encodings from given HTTP Header Dict.

    :param headers: dictionary to extract encoding from.
    :rtype: str
    """

    content_type = headers.get('content-type')

    if not content_type:
        return None

    content_type, params = _parse_content_type_header(content_type)

    if 'charset' in params:
        return params['charset'].strip("'\"")

    if 'text' in content_type:
        return 'ISO-8859-1'

    if 'application/json' in content_type:
        # Assume UTF-8 based on RFC 4627: https://www.ietf.org/rfc/rfc4627.txt since the charset was unset
        return 'utf-8'


def filter_query(
    query: str,
    stripEmpty: typing.Optional[bool] = False,
    stripDuplicates: typing.Optional[bool] = False
) -> str:

    params = []
    names = []

    for param in query.split(sep="&"):
        # Ignore empty fields
        if not param:
            continue

        key, *values = param.split(sep="=")
        
        value = "%3D".join(values)
        value = value.replace("?", "%3F")
        
        # Ignore field with empty value
        if stripEmpty and not value:
            continue
        
        # Ignore field with duplicate name
        if stripDuplicates and key in names:
            continue
        
        params.append(f"{key}={value}" if value or "=" in param else key)
        
        names.append(key)

    return "&".join(params)
