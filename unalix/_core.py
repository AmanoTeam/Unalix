from http.cookiejar import CookieJar
import json
import re
from urllib.parse import unquote, urlparse, urlunparse

from ._config import (
    allow_all_cookies,
    deny_all_cookies,
    allow_cookies_if_needed,
    allowed_mimes,
    allowed_schemes,
    default_headers,
    max_redirects,
    paths_data,
    paths_redirects
)
from ._exceptions import ConnectionError, InvalidURL, InvalidScheme, TooManyRedirects
from ._http import add_missing_attributes, create_connection, handle_redirects, get_encoded_content
from ._utils import (
    is_private,
    prepend_scheme_if_needed,
    remove_invalid_parameters,
    requote_uri,
    strip_parameters,
    urldefragauth
)

def parse_url(url):
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
        raise InvalidURL("This is not a valid URL", url)

    # If the specified URL does not have a scheme defined, it will be set to 'http'.
    url = prepend_scheme_if_needed(url, "http")

    # Remove the fragment and the authentication part (e.g 'user:pass@') from the URL.
    url = urldefragauth(url)

    scheme, netloc, path, params, query, fragment = urlparse(url)

    # We don't want to process URLs with protocols other than those
    if scheme not in allowed_schemes:
        raise InvalidScheme(f"Expecting 'http' or 'https', but got: {scheme}")

    # Encode domain name according to IDNA.
    netloc = netloc.encode("idna").decode('utf-8')

    return urlunparse((
        scheme, netloc, path, params, query, fragment
    ))

def extract_url(url, response):
    """This function is used to extract redirect links from HTML pages."""
    content_type = response.headers.get("Content-Type")

    if content_type is None:
        return None

    mime = strip_parameters(content_type)

    if mime not in allowed_mimes:
        return None

    body = get_encoded_content(response)

    for pattern, redirect_list in redirects:
        if pattern.match(url):
            for redirect in redirect_list:
                try:
                    result = redirect.match(body)
                    extracted_url = result.group(1)
                except AttributeError:
                    continue
                else:
                    return extracted_url

    return None

def clear_url(url, **kwargs):
    """Remove tracking fields from the given URL.

    Parameters:
        url (`str`):
            Some URL with tracking fields.

        **kwargs (`bool`, *optional*):
            Optional arguments that `parse_rules` takes.

    Raises:
        InvalidURL: In case the provided *url* is not a valid URL or hostname.

        InvalidScheme: In case the provided *url* has a invalid or unknown scheme.

    Usage:
      >>> from unalix import clear_url
      >>> clear_url("https://deezer.com/track/891177062?utm_source=deezer")
      'https://deezer.com/track/891177062'
    """
    return parse_rules(parse_url(url), **kwargs)

def unshort_url(url, parse_documents = False, enable_cookies = None, **kwargs):
    """Try to unshort the given URL (follow http redirects).

    Parameters:
        url (`str`):
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

        **kwargs (`bool`, *optional*):
            Optional arguments that `parse_rules` takes.

    Raises:
        ConnectionError: In case some error occurred during the request.

        TooManyRedirects: In case the request exceeded maximum allowed redirects.

        InvalidURL: In case the provided *url* is not a valid URL or hostname.

        InvalidScheme: In case the provided *url* has a invalid or unknown scheme.

        InvalidContentEncoding: In case the HTTP response has a invalid "Content-Enconding" header.

    Usage:
      >>> from unalix import unshort_url
      >>> unshort_url("https://bitly.is/Pricing-Pop-Up")
      'https://bitly.com/pages/pricing'
    """
    url = parse_rules(parse_url(url), **kwargs)

    if enable_cookies is None:
        cookies = CookieJar(policy=allow_cookies_if_needed)
    elif enable_cookies is True:
        cookies = CookieJar(policy=allow_all_cookies)
    elif enable_cookies is False:
        cookies = CookieJar(policy=deny_all_cookies)

    total_redirects = 0

    while True:

        if total_redirects > max_redirects:
            raise TooManyRedirects("The request exceeded maximum allowed redirects", url)

        scheme, netloc, path, params, query, fragment = urlparse(url)
        connection = create_connection(scheme, netloc)

        add_missing_attributes(url, connection) 

        if query:
            path = f"{path}?{query}"

        cookies.add_cookie_header(connection)

        headers = connection.headers
        headers.update(default_headers)

        try:
            connection.request("GET", path, headers=headers)
            response = connection.getresponse()
        except Exception as exception:
            raise ConnectionError(str(exception), url)

        cookies.extract_cookies(response, connection)

        redirect_url = handle_redirects(url, response)

        if isinstance(redirect_url, str):
            total_redirects = total_redirects + 1
            url = parse_rules(redirect_url, **kwargs)
            continue

        if parse_documents:
            extracted_url = extract_url(url, response)
            if isinstance(extracted_url, str):
                url = parse_rules(extracted_url, **kwargs)
                continue

        break

    if not response.isclosed():
        response.close()

    return url

def compile_rules(files):

    compiled_data_as_tuple = []

    for filename in files:
        with open(filename, mode="r", encoding="utf-8") as file_object:
            content = file_object.read()
            dict_rules = json.loads(content)

        for provider in dict_rules["providers"].keys():
            exceptions, redirections, rules, referrals, raws = [], [], [], [], []

            for exception in dict_rules["providers"][provider]["exceptions"]:
                exceptions += [
                    re.compile(exception)
                ]

            for redirection in dict_rules["providers"][provider]["redirections"]:
                redirections += [
                    re.compile(f"{redirection}.*")
                ]

            for common in dict_rules["providers"][provider]["rules"]:
                rules += [
                    re.compile(rf"(%(?:26|23)|&|#|^){common}(?:(?:=|%3[Dd])[^&]*)")
                ]

            for referral in dict_rules["providers"][provider]["referralMarketing"]:
                referrals += [
                    re.compile(rf"(%(?:26|23)|&|#|^){referral}(?:(?:=|%3[Dd])[^&]*)")
                ]

            for raw in dict_rules["providers"][provider]["rawRules"]:
                raws += [
                    re.compile(raw)
                ]

            compiled_data_as_tuple += [
                (
                    re.compile(dict_rules["providers"][provider]["urlPattern"]),
                    dict_rules["providers"][provider]["completeProvider"],
                    rules,
                    referrals,
                    exceptions,
                    raws,
                    redirections
                )
            ]

    return compiled_data_as_tuple

def compile_redirects(files):

    compiled_data_as_tuple = []

    for filename in files:
        with open(filename, mode="r", encoding="utf-8") as file_object:
            content = file_object.read()
            dict_rules = json.loads(content)

        for rule in dict_rules:
            redirects_list = []

            for raw_pattern in rule["redirects"]:
                redirects_list += [
                    re.compile(f".*{raw_pattern}.*", flags=re.MULTILINE|re.DOTALL)
                ]

            compiled_data_as_tuple += [
                (
                    re.compile(rule["pattern"]),
                    redirects_list
                )
            ]

    return compiled_data_as_tuple

def parse_rules(
    url,
    allow_referral = False,
    ignore_rules = False,
    ignore_exceptions = False,
    ignore_raw = False,
    ignore_redirections = False,
    skip_blocked = False,
    skip_local = False
):
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
    kwargs = locals()
    del kwargs["url"]

    for (pattern, complete, rules, referrals, exceptions, raws, redirections) in patterns:

        scheme, netloc, path, params, query, fragment = urlparse(url)

        if skip_local and is_private(netloc):
            return url

        if skip_blocked and complete:
            continue

        original_url, skip_provider = url, False

        if pattern.match(f"{scheme}://{netloc}"):

            if not ignore_exceptions:
                for exception in exceptions:
                    if exception.match(url):
                        skip_provider = True
                        break

            if skip_provider:
                continue

            if not ignore_redirections:
                for redirection in redirections:
                    url = redirection.sub(r"\g<1>", url)
                if url != original_url:
                    url = requote_uri(unquote(url))
                    return parse_rules(url, **kwargs)

            if query:
                if not ignore_rules:
                    for rule in rules:
                        query = rule.sub(r"\g<1>", query)
                if not allow_referral:
                    for referral in referrals:
                        query = referral.sub(r"\g<1>", query)

            if path:
                if not ignore_raw:
                    for raw in raws:
                        path = raw.sub("", path)

            url = urlunparse((
                scheme, netloc, path, params, query, fragment
            ))

    return remove_invalid_parameters(url)

patterns = compile_rules(paths_data)
redirects = compile_redirects(paths_redirects)