from http.client import HTTPResponse
from http.cookiejar import CookieJar
from ipaddress import ip_address
import json
import re
from typing import List, Tuple, Any, Union
from urllib.parse import quote, unquote, urlparse, urlunparse, ParseResult

from ._config import (
    allow_all_cookies,
    deny_all_cookies,
    allow_cookies_if_needed,
    allowed_mimes,
    allowed_schemes,
    default_headers,
    local_domains,
    max_redirects,
    paths_data,
    paths_redirects,
    replacements,
    loop
)
from ._exceptions import InvalidURL, InvalidScheme, InvalidList, TooManyRedirects
from ._http import add_missing_attributes, create_connection, handle_redirects, get_encoded_content

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L566
# The unreserved URI characters (RFC 3986)
UNRESERVED_SET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789-._~")

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L570
async def unquote_unreserved(uri: str) -> str:
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
async def requote_uri(uri: str) -> str:
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
        return quote(await unquote_unreserved(uri), safe=safe_with_percent)
    except ValueError:
        # We couldn't unquote the given URI, so let"s try quoting it, but
        # there may be unquoted "%"s in the URI. We need to make sure they're
        # properly quoted so they do not cause issues elsewhere.
        return quote(uri, safe=safe_without_percent)

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L894
async def prepend_scheme_if_needed(url: str, new_scheme: str) -> str:
    """Given a URL that may or may not have a scheme, prepend the given scheme.
    Does not replace a present scheme with the one provided as an argument.
    """
    scheme, netloc, path, params, query, fragment = urlparse(url, new_scheme)

    # urlparse is a finicky beast, and sometimes decides that there isn't a
    # netloc present. Assume that it's being over-cautious, and switch netloc
    # and path if urlparse decided there was no netloc.
    if not netloc:
        netloc, path = path, netloc

    return urlunparse((scheme, netloc, path, params, query, fragment))

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L953
async def urldefragauth(url: str) -> str:
    """Given a url remove the fragment and the authentication part."""
    scheme, netloc, path, params, query, fragment = urlparse(url)

    # see func:`prepend_scheme_if_needed`
    if not netloc:
        netloc, path = path, netloc

    netloc = netloc.rsplit("@", 1)[-1]

    return urlunparse((scheme, netloc, path, params, query, ''))

async def is_private(url: str) -> bool:
    """This function checks if the URL's netloc belongs to a local/private network.

    Usage:
      >>> from unalix._utils import is_private
      >>> is_private("http://0.0.0.0/")
      True
    """
    netloc = urlparse(url).netloc
    
    try:
        address = ip_address(netloc)
    except ValueError:
        return (netloc in local_domains)
    else:
        return address.is_private

async def parse_url(url: str) -> str:
    """Parse and format the given URL.

    This function has three purposes:

    - Add the "http://" prefix if the *url* provided does not have a defined scheme.
    - Convert domain names in non-Latin alphabet to punycode.
    - Remove the fragment and the authentication part (e.g 'user:pass@') from the URL.

    Parameters:
        url (`str`):
            Full URL or hostname.

    Raises:
        InvalidURL: In case the provided *url* is not a valid URL or hostname.

        InvalidScheme: In case the provided *url* has a invalid or unknown scheme.

    Usage:
      >>> from unalix._utils import parse_url
      >>> parse_url("i❤️.ws")
      'http://xn--i-7iq.ws/'
    """
    if not isinstance(url, str) or not url:
        raise InvalidURL("This is not a valid URL")

    # If the specified URL does not have a scheme defined, it will be set to 'http'.
    url = await prepend_scheme_if_needed(url, "http")

    # Remove the fragment and the authentication part (e.g 'user:pass@') from the URL.
    url = await urldefragauth(url)

    scheme, netloc, path, params, query, fragment = urlparse(url)
    
    # We don't want to process URLs with protocols other than those
    if not scheme in allowed_schemes:
        raise InvalidScheme(f"Expecting 'http' or 'https', but got: {scheme}")

    # Encode domain name according to IDNA.
    netloc = netloc.encode("idna").decode('utf-8')

    return urlunparse((scheme, netloc, path, params, query, fragment))

async def clear_url(url: Union[str, ParseResult], **kwargs) ->  Union[str, ParseResult]:
    """Remove tracking fields from the given URL.

    Parameters:
        url (`str` | `ParseResult`):
            Some URL with tracking fields.

        **kwargs (`bool`, *optional*):
            Optional arguments that `parse_rules` takes.

    Raises:
        InvalidURL: In case the provided *url* is not a valid URL or hostname.

        InvalidScheme: In case the provided *url* has a invalid or unknown scheme.

    Notes:
        URL formatting will not be performed  if the provided *url* is a instance of `ParseResult`. In that case,
        "InvalidURL" and "InvalidScheme" will not be raised, even if the *url* has a invalid value.

    Usage:
      >>> from unalix import clear_url
      >>> clear_url("https://deezer.com/track/891177062?utm_source=deezer")
      'https://deezer.com/track/891177062'
    """
    if isinstance(url, ParseResult):
        cleaned_url = await parse_rules(url.geturl())
        return urlparse(cleaned_url)

    formated_url = await parse_url(url)
    cleaned_url = await parse_rules(formated_url, **kwargs)

    return cleaned_url

async def strip_parameters(value: str) -> str:
    """This function is used strip parameters from header values."""
    return value.rsplit(";", 1)[0].rstrip(" ")

async def extract_url(url: ParseResult, response: HTTPResponse) -> ParseResult:
    """This function is used to extract redirect links from HTML pages."""
    content_type = response.headers.get("Content-Type")

    if content_type is None:
        return url

    mime = await strip_parameters(content_type)

    if not mime in allowed_mimes:
        return url

    body = await get_encoded_content(response)

    for rule in redirects:
        if rule["pattern"].match(url.geturl()):
            for redirect in rule["redirects"]:
                try:
                    result = redirect.match(body)
                    extracted_url = result.group(1)
                except AttributeError:
                    continue
                else:
                    return urlparse(extracted_url)

    return url

async def unshort_url(
    url: Union[str, ParseResult],
    parse_documents: bool = False,
    enable_cookies: Union[bool, None] = None,
    headers: dict = default_headers,
    **kwargs
) -> Union[str, ParseResult]:
    """Try to unshort the given URL (follow http redirects).

    Parameters:
        url (`str`| `ParseResult`):
            Shortened URL.

        parse_documents (`bool`, *optional*):
            If True, Unalix will also try to obtain the unshortened URL from the response's body.

        enable_cookies (`bool`, *optional*):
            True: Unalix will handle cookies for all requests.
            False: Unalix will not handle cookies.
            None (default): Unalix will handle cookies only if needed.

            In most cases, cookies returned in HTTP responses are useless. They do not need to be stored
            or sent back to the server. However, there are some cases where they are still required.

            Keeping this as "None" should be enough for you. Only set this parameter to True if you get stuck
            at some redirect loop due to missing cookies.

        headers (`dict`, *optional*):
            Default headers for HTTP requests.

        **kwargs (`bool`, *optional*):
            Optional arguments that `clear_url` takes.

    Raises:
        InvalidURL: In case the provided *url* is not a valid URL or hostname.

        InvalidScheme: In case the provided *url* has a invalid or unknown scheme.

        InvalidContentEncoding: In case the HTTP response has a invalid "Content-Enconding" header.

        TooManyRedirects: In case some request exceeds the maximum number of allowed redirects.

    Notes:
        URL formatting will not be performed  if the provided *url* is a instance of `ParseResult`. In that case,
        "InvalidURL" and "InvalidScheme" will not be raised, even if the *url* has a invalid value.

    Usage:
      >>> from unalix import unshort_url
      >>> unshort_url("https://bitly.is/Pricing-Pop-Up")
      'https://bitly.com/pages/pricing'
    """
    cleaned_url = await clear_url(url, **kwargs)

    if isinstance(cleaned_url, ParseResult):
        parsed_url = cleaned_url
    else:
        parsed_url = urlparse(cleaned_url)

    cookies = CookieJar()

    if enable_cookies == None:
        cookies.set_policy(allow_cookies_if_needed)
    elif enable_cookies == True:
        cookies.set_policy(allow_all_cookies)
    elif enable_cookies == False:
        cookies.set_policy(deny_all_cookies)

    total_redirects = 0

    while True:
        if total_redirects >= max_redirects:
            raise TooManyRedirects("Exceeded maximum allowed redirects.")
        
        scheme, netloc, path, params, query, fragment = parsed_url
        connection = await create_connection(scheme, netloc)

        await add_missing_attributes(parsed_url, headers, connection)

        if query: path = f"{path}?{query}"

        cookies.add_cookie_header(connection)

        connection.request("GET", path, headers=headers)
        response = connection.getresponse()

        cookies.extract_cookies(response, connection)

        redirect_url = await handle_redirects(parsed_url, response) # type: ignore
        requoted_uri = urlparse(await requote_uri(urlunparse(redirect_url)))

        if requoted_uri != parsed_url:
            total_redirects = total_redirects + 1
            parsed_url = await clear_url(requoted_uri, **kwargs)
            continue

        if parse_documents:
            extracted_url = await extract_url(parsed_url, response) # type: ignore
            requoted_uri = urlparse(await requote_uri(extracted_url.geturl()))
            if extracted_url != parsed_url:
                parsed_url = await clear_url(requoted_uri)
                continue

        break

    if not response.isclosed():
        response.close()

    if isinstance(url, ParseResult):
        return parsed_url
    else:
        return urlunparse(parsed_url)

async def compile_patterns(
    data: List[str],
    replacements: List[Tuple[str, str]],
    redirects: List[str]
) -> Tuple[List[Any], List[Any], List[Any]]:
    """Compile raw regex patterns into `re.Pattern` instances.

    Parameters:
        data (`list`):
            List containing one or more paths to "data.min.json" files.

        replacements (`list`):
            List containing one or more tuples of raw regex patterns.

        redirects (`list`):
            List containing one or more paths to "body_redirects.json" files.

    Raises:
        InvalidList: In case the provided *files* or *replacements* are not a valid list.
    """
    if not isinstance(data, list) or not data:
        raise InvalidList("Invalid file list")

    if not isinstance(replacements, list) or not replacements:
        raise InvalidList("Invalid replacements list")

    compiled_data = []
    compiled_replacements = []
    compiled_redirects = []

    for filename in data:
        with open(filename, mode="r", encoding="utf-8") as file_object:
            dict_rules = json.loads(file_object.read())
        for provider in dict_rules["providers"].keys():
            (exceptions, redirections, rules, referrals, raws) = ([], [], [], [], [])
            for exception in dict_rules["providers"][provider]["exceptions"]:
                exceptions += [re.compile(exception)]
            for redirection in dict_rules["providers"][provider]["redirections"]:
                redirections += [re.compile(f"{redirection}.*")]
            for common in dict_rules["providers"][provider]["rules"]:
                rules += [re.compile(rf"(%(?:26|23|3[Ff])|&|#|\?){common}(?:(?:=|%3[Dd])[^&]*)")]
            for referral in dict_rules["providers"][provider]["referralMarketing"]:
                referrals += [re.compile(rf"(%(?:26|23|3[Ff])|&|#|\?){referral}(?:(?:=|%3[Dd])[^&]*)")]
            for raw in dict_rules["providers"][provider]["rawRules"]:
                raws += [re.compile(raw)]
            compiled_data += [{
                "pattern": re.compile(dict_rules["providers"][provider]["urlPattern"]),
                "complete": dict_rules["providers"][provider]["completeProvider"],
                "redirection": dict_rules["providers"][provider]["forceRedirection"],
                "exceptions": exceptions,
                "redirections": redirections,
                "rules": rules,
                "referrals": referrals,
                "raws": raws
            }]

    for pattern, replacement in replacements:
        compiled_replacements += [(re.compile(pattern), replacement)]

    for filename in redirects:
        with open(filename, mode="r", encoding="utf-8") as file_object:
            dict_rules = json.loads(file_object.read())
        for rule in dict_rules:
            redirects_list = []
            for raw_pattern in rule["redirects"]:
                redirects_list += [re.compile(f".*{raw_pattern}.*", flags=re.MULTILINE|re.DOTALL)]
            compiled_redirects += [{
                "pattern": re.compile(rule["pattern"]),
                "redirects": redirects_list
            }]

    return (compiled_data, compiled_replacements, compiled_redirects)

async def parse_rules(
    url: str,
    allow_referral: bool = False,
    ignore_rules: bool = False,
    ignore_exceptions: bool = False,
    ignore_raw: bool = False,
    ignore_redirections: bool = False,
    skip_blocked: bool = False,
    skip_local: bool = False
) -> str:
    """Parse compiled regex patterns for the given URL.

    Please take a look at:
        https://github.com/ClearURLs/Addon/wiki/Rules
    to understand how these rules are processed.

    Parameters:
        url (`str`):
            Some URL with tracking fields.

        allow_referral (`bool`, *optional*):
            Pass True to ignore regex rules targeting marketing fields.

        ignore_rules (`bool`, *optional*):
            Pass True to ignore regex rules from "rules" keys.

        ignore_exceptions (`bool`, *optional*):
            Pass True to ignore regex rules from "exceptions" keys.

        ignore_raw (`bool`, *optional*):
            Pass True to ignore regex rules from "rawRules" keys.

        ignore_redirections (`bool`, *optional*):
            Pass True to ignore regex rules from "redirections" keys.

        skip_blocked (`bool`, *optional*):
            Pass True to skip/ignore regex rules for blocked domains.

        skip_local (`bool`, *optional*):
            Pass True to skip URLs on local/private hosts (e.g 127.0.0.1, 0.0.0.0, localhost).

    Notes:
        Note that most of the regex patterns contained in the
        "urlPattern", "redirections" and "exceptions" keys expects
        all given URLs to starts with the prefixe "http://" or "https://".

    Usage:
      >>> from unalix._utils import parse_rules
      >>> parse_rules("http://g.co/?utm_source=google")
      'http://g.co/'
    """
    if skip_local and await is_private(url):
        return url

    for pattern in patterns:
        if skip_blocked and pattern["complete"]:
            continue
        (original_url, skip_provider) = (url, False)
        if pattern["pattern"].match(url):
            if not ignore_exceptions:
                for exception in pattern["exceptions"]:
                    if exception.match(url):
                        skip_provider = True
                        break
            if skip_provider:
                continue
            if not ignore_redirections:
                for redirection in pattern["redirections"]:
                    url = redirection.sub(r"\g<1>", url)
                if url != original_url:
                    url = unquote(url)
                    url = await requote_uri(url)
            if not ignore_rules:
                for rule in pattern["rules"]:
                    url = rule.sub(r"\g<1>", url)
            if not allow_referral:
                for referral in pattern["referrals"]:
                    url = referral.sub(r"\g<1>", url)
            if not ignore_raw:
                for raw in pattern["raws"]:
                    url = raw.sub("", url)
            original_url = url

    for pattern, replacement in replacements:
        url = pattern.sub(replacement, url)

    return url

(patterns, replacements, redirects) = loop.run_until_complete(compile_patterns(paths_data, replacements, paths_redirects))
