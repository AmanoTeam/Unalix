import html
import json
import os
import random
import re
from urllib.parse import quote, unquote, urlparse, urlunparse

from ._config import (
    httpopt,
    data_min,
    body_redirects
)
from ._exceptions import ConnectError, InvalidURL, InvalidScheme, TooManyRedirects
from ._http import (
    add_missing_attributes,
    create_connection,
    create_cookie_jar,
    handle_redirects
)
from ._utils import (
    is_private,
    prepend_scheme_if_needed,
    remove_invalid_parameters,
    requote_uri
)

def parse_url(url):
    """Parse and format the given URL.

    This function has three purposes:

    - Add the "http://" prefix if the *url* provided does not have a defined scheme.
    - Convert domain names in non-Latin alphabet to punycode.

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
        raise InvalidURL(message="This is not a valid URL", url=url)

    scheme, netloc, path, params, query, fragment = urlparse(
        prepend_scheme_if_needed(url, "http")
    )

    # We don't want to process URLs with protocols other than those
    if scheme not in ("http", "https"):
        raise InvalidScheme(message=f"Expecting 'http' or 'https', but got: {scheme}", url=url)

    # Encode domain name according to IDNA.
    netloc = netloc.encode(encoding="idna").decode(encoding='utf-8')

    return urlunparse((
        scheme, netloc, path, params, query, fragment
    ))


def extract_url(url, response):
    """This function is used to extract redirect links from HTML pages."""
    body = response.read()

    scheme, netloc, path, params, query, fragment = urlparse(url)

    matched = None

    for patterns, domains, rules in redirects:
        if netloc in domains:
            matched = True
        else:
            for pattern in patterns:
                if pattern.match(url):
                    matched = True
                    break

        if matched:
            for rule in rules:
                result = rule.match(body.decode())
                if result is None:
                    continue
                else:
                    extracted_url = result.group(1)
                    return parse_extracted_url(extracted_url)


def parse_extracted_url(url):
    return parse_url(requote_uri(html.unescape(url)))


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


def unshort_url(url, parse_documents=False, cookie_policy="allow_if_needed", **kwargs):
    """Try to unshort the given URL (follow http redirects).

    Parameters:
        url (`str`):
            Shortened URL.

        parse_documents (`bool`, *optional*):
            If True, Unalix will also try to obtain the unshortened URL from the
            response's body.

        cookie_policy (`str`, *optional*):
            "allow_all": Unalix will handle cookies for all requests.
            "allow_if_needed" (default): Unalix will handle cookies only if needed.
            "reject_all": Unalix will not handle cookies.

            In most cases, cookies returned in HTTP responses are useless.
            They do not need to be stored or sent back to the server.

            Keeping this as "None" should be enough for you. Only set this parameter
            to True if you get stuck at some redirect loop due to missing cookies.

        **kwargs (`bool`, *optional*):
            Optional arguments that `parse_rules` takes.

    Raises:
        ConnectError: In case some error occurred during the request.

        TooManyRedirects: In case the request exceeded maximum allowed redirects.

        InvalidURL: In case the provided *url* is not a valid URL or hostname.

        InvalidScheme: In case the provided *url* has a invalid or unknown scheme.

    Usage:
      >>> from unalix import unshort_url
      >>> unshort_url("https://bitly.is/Pricing-Pop-Up")
      'https://bitly.com/pages/pricing'
    """
    url, cookies, total_redirects = (
        parse_rules(parse_url(url), **kwargs),
        create_cookie_jar(policy_type=cookie_policy),
        0
    )

    while True:

        if total_redirects > httpopt.max_redirects:
            raise TooManyRedirects(
                message="The request exceeded maximum allowed redirects",
                url=url
            )

        scheme, netloc, path, params, query, fragment = urlparse(url)
        connection = create_connection(scheme, netloc)

        add_missing_attributes(url, connection)

        if query:
            path = f"{path}?{query}"

        cookies.add_cookie_header(connection)

        connection.headers.update(httpopt.headers)
        
        headers = connection.headers

        try:
            connection.request("GET", path, headers=headers)
            response = connection.getresponse()
        except Exception as exception:
            raise ConnectError(
                message=str(exception),
                exception=exception,
                url=url
            )

        cookies.extract_cookies(response, connection)

        redirect_url = handle_redirects(url, response)

        if isinstance(redirect_url, str):
            total_redirects += 1
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

    for file in files:
        with open(file=file, mode="r", encoding="utf-8") as jfile:
            content = jfile.read()

        ruleset = json.loads(content)["providers"]

        for provider in ruleset:
            pattern, complete_provider = (
                re.compile(pattern=ruleset[provider]["urlPattern"]),
                ruleset[provider]["completeProvider"]
            )
            exceptions, redirections, rules, referrals, raws = (
                [], [], [], [], []
            )

            for exception in ruleset[provider]["exceptions"]:
                exceptions.append(
                    re.compile(pattern=exception)
                )

            for redirection in ruleset[provider]["redirections"]:
                redirections.append(
                    re.compile(pattern=f"{redirection}.*")
                )

            for rule in ruleset[provider]["rules"]:
                rules.append(
                    re.compile(pattern=rf"(%(?:26|23)|&|^){rule}(?:(?:=|%3[Dd])[^&]*)")
                )

            for referral in ruleset[provider]["referralMarketing"]:
                referrals.append(
                    re.compile(pattern=rf"(%(?:26|23)|&|^){referral}(?:(?:=|%3[Dd])[^&]*)")
                )

            for raw in ruleset[provider]["rawRules"]:
                raws.append(
                    re.compile(pattern=raw)
                )

            compiled_data_as_tuple.append(
                (
                    pattern,
                    complete_provider,
                    rules,
                    referrals,
                    exceptions,
                    raws,
                    redirections
                )
            )

    return compiled_data_as_tuple


def compile_redirects(files):

    compiled_data_as_tuple = []

    for file in files:
        with open(file=file, mode="r", encoding="utf-8") as jfile:
            content = jfile.read()

        ruleset = json.loads(content)

        for rule in ruleset:
            patterns, domains, redirects = (
                rule["patterns"],
                rule["domains"],
                rule["redirects"]
            )
            new_patterns, new_redirects = [], []

            for pattern in patterns:
                new_patterns.append(
                    re.compile(pattern=pattern)
                )

            for redirect in redirects:
                new_redirects.append(
                    re.compile(pattern=f".*{redirect}.*", flags=re.MULTILINE | re.DOTALL)
                )

            compiled_data_as_tuple.append(
                (
                    new_patterns,
                    domains,
                    new_redirects
                )
            )

    return compiled_data_as_tuple


def randomize_query(query, rules):

    randomized, not_randomized, query = (
        {}, {}, query.split(sep="&")
    )

    for entrie in query:
        try:
            key, value = entrie.split(sep="=")
        except ValueError:
            continue
        else:
            for rule in rules:
                if rule.match(entrie):
                    bytes_count = random.randint(3, 7)
                    randomized.update(
                        {
                            key: quote(os.urandom(bytes_count))
                        }
                    )
                    break
            else:
                not_randomized.update(
                    {
                        key: value
                    }
                )

    new_query = []

    for key, value in not_randomized.items():
        new_query.append(f"{key}={value}")

    for key, value in randomized.items():
        new_query.append(f"{key}={value}")

    return "&".join(new_query)


def parse_rules(
    url,
    allow_referral=False,
    ignore_rules=False,
    ignore_exceptions=False,
    ignore_raw=False,
    ignore_redirections=False,
    skip_blocked=False,
    skip_local=False,
    block_mode="block_everything"
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
            Pass True to skip URLs on local/private hosts (e.g. 127.0.0.1, 0.0.0.0).

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
    kwargs.pop("url")

    for ( pattern, complete, rules, referrals,
            exceptions, raws, redirections ) in patterns:

        scheme, netloc, path, params, query, fragment = urlparse(
            prepend_scheme_if_needed(url, "http")
        )

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
                    if block_mode == "fake_everything":
                        query = randomize_query(query, rules)
                    else:
                        for rule in rules:
                            query = rule.sub(r"\g<1>", query)
                if not allow_referral:
                    if block_mode == "fake_everything":
                        query = randomize_query(query, referrals)
                    else:
                        for referral in referrals:
                            query = referral.sub(r"\g<1>", query)

            if path:
                if not ignore_raw:
                    for raw in raws:
                        path = raw.sub("", path)

            url = urlunparse(
                (scheme, netloc, path, params, query, fragment)
            )

    return remove_invalid_parameters(url)


patterns = compile_rules(data_min)
redirects = compile_redirects(body_redirects)
