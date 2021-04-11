import typing
import http.cookiejar
import http.client
import ssl
import html
import urllib.parse
import time
import datetime

from .. import types
from .. import config

from .. import utils
from .. import exceptions

from . import cookie_policies
from . import ssl_context
from . import url_cleaner
from . import coreutils

body_redirects = coreutils.body_redirects_from_files(config.PATH_BODY_REDIRECTS)

def unshort_url(
    url: typing.Union[str, urllib.parse.ParseResult],
    parse_documents: typing.Optional[bool] = False,
    max_redirects: typing.Optional[int] = None,
    timeout: typing.Optional[int] = None,
    headers: typing.Optional[typing.Dict[str, str]] = None,
    max_fetch_size: typing.Optional[int] = None,
    cookie_policy: typing.Optional[http.cookiejar.DefaultCookiePolicy] = None,
    context: typing.Optional[ssl.SSLContext] = None,
    max_retries:  typing.Optional[int] = None,
    status_retry:  typing.Optional[typing.Iterable[typing.Union[int, http.HTTPStatus]]] = None,
    **kwargs
):
    """
    This method implements a simple HTTP 1.1 client, mainly used to follow HTTP redirects and read responses body.
    We ensure that all redirect URLs are cleaned before we follow them.

    Parameters:

        url (str):
            A string representing an HTTP URL.

        parse_documents (bool | optional):
            Pass True to instruct Unalix to look for redirect URLs in the response body when there is no HTTP redirects
            to follow. Defaults to False.

            This method is unstable and sometimes can return broken or incomplete URLs. Use with caution.

        max_redirects (int | optional):
            Max number of HTTP redirects to follow before raising an exception. Defaults to unalix.config.HTTP_MAX_REDIRECTS.

            Redirects followed from the response body also counts.

        timeout (int | optional):
            Max number of seconds to wait for a response before raising an exception. Defaults to unalix.config.HTTP_TIMEOUT.

        headers (dict | optional):
            HTTP request headers as {"key": "value"}. Defaults to unalix.config.HTTP_HEADERS.

        max_fetch_size (int | optional):
            How many bytes to fetch from response body. Defaults to unalix.config.HTTP_MAX_FETCH_SIZE.

        cookie_policy (http.cookiejar.DefaultCookiePolicy | optional):
            Custom cookie policy for cookie handling. Defaults to unalix.COOKIE_STRICT_ALLOW.

            Note that cookies are not shared between sessions. Each call to unshort_url() will
            create it's own http.cookiejar.CookieJar() instance.

            unalix.COOKIE_STRICT_ALLOW is a strict policy which only allow cookies from sites that where known to not
            work without them.

        context (ssl.SSLContext | optional):
            Custom SSL context for HTTPS connections. Defaults to unalix.SSL_CONTEXT_VERIFIED.

        max_retries (int | optional):
            Max number of times to retry on connection errors. Defaults to unalix.config.HTTP_MAX_RETRIES.

        status_retry (typing.Iterable | optional):
            List or iterable of http status code to retry on. Defaults to unalix.config.HTTP_STATUS_RETRY.

            Only takes effect when max_retries > 0.

        **kwargs (optional):
            Optional keyword arguments that unalix.clear_url() takes.

    Usage examples:

        Rejecting all cookies

            >>> from unalix import unshort_url, COOKIE_REJECT_ALL
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> unshort_url(url, cookie_policy=COOKIE_REJECT_ALL)
            'https://bitly.com/pages/pricing'

      Allowing all cookies

            >>> from unalix import unshort_url, COOKIE_ALLOW_ALL
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> unshort_url(url, cookie_policy=COOKIE_ALLOW_ALL)
            'https://bitly.com/pages/pricing'

      Disabling SSL certificate validation

            >>> from unalix import unshort_url, SSL_CONTEXT_UNVERIFIED
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> unshort_url(url, context=SSL_CONTEXT_UNVERIFIED)
            'https://bitly.com/pages/pricing'
    """

    cookie_jar = http.cookiejar.CookieJar()
    cookie_jar.set_policy(
        cookie_policy if cookie_policy is not None else cookie_policies.COOKIE_STRICT_ALLOW
    )

    total_redirects = 0
    total_retries = 0

    while True:

        if total_redirects > (max_redirects if max_redirects is not None else config.HTTP_MAX_REDIRECTS):
            raise exceptions.TooManyRedirectsError(
                message="Exceeded maximum allowed redirects",
                url=url
            ) from None

        if total_retries > (max_retries if max_retries is not None else config.HTTP_MAX_RETRIES):
            raise exceptions.MaxRetriesError(
                message="Exceeded maximum allowed retries",
                url=url
            ) from None

        if isinstance(url, (types.URL, urllib.parse.ParseResult)):
            url = types.URL(url.geturl())
        else:
            url = types.URL(url)

        if url.scheme == "http":
            connection = http.client.HTTPConnection(
                host=url.netloc,
                port=url.port,
                timeout=timeout if timeout is not None else config.HTTP_TIMEOUT
            )
        elif url.scheme == "https":
            connection = http.client.HTTPSConnection(
                host=url.netloc,
                port=url.port,
                timeout=timeout if timeout is not None else config.HTTP_TIMEOUT,
                context=context if context is not None else ssl_context.SSL_CONTEXT_VERIFIED
            )
        else:
            raise exceptions.UnsupportedProtocolError(
                message="Unsupported or invalid scheme found in URL",
                url=url
            ) from None

        # Workaround for making http.client's connection objects compatible with the
        # http.cookiejar.CookieJar's extract_cookies() and add_cookie_header() methods.

        connection.unverifiable = True

        connection.has_header = lambda header_name: False
        connection.get_full_url = lambda: str(url)

        connection.origin_req_host = url.netloc

        connection.headers = {}
        connection.cookies = {}

        def add_unredirected_header(key, value):
            connection.headers.update({key: value})

        connection.add_unredirected_header = add_unredirected_header

        cookie_jar.add_cookie_header(connection)

        # Merge headers added by cookie_jar.add_cookie_header() with default headers
        connection_headers = headers if headers is not None else dict(config.HTTP_HEADERS)
        connection_headers.update(connection.headers)

        try:
            connection.request(
                method="GET",
                url=f"{url.path}?{url.query}" if url.query else url.path,
                headers=connection_headers
            )
            response = connection.getresponse()
        except Exception as exception:
            connection.close()
            
            # Retry based on connection error
            if (max_retries if max_retries is not None else config.HTTP_MAX_RETRIES) != 0:
                total_retries += 1
                continue
            else:
                raise exceptions.ConnectError(
                    message="Connection error",
                    url=url
                ) from exception
        else:
            # Retry based on status code
            if (max_retries if max_retries is not None else config.HTTP_MAX_RETRIES) != 0 and response.code in (status_retry if status_retry is not None else config.HTTP_STATUS_RETRY):
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None:
                    if retry_after.isnumeric():
                        time.sleep(int(retry_after))
                    else:
                        http_date = datetime.datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S GMT")
                        time.sleep(int(http_date.timestamp()) - int(time.time()))
                
                total_retries += 1
                
                continue

        # Extract cookies from response
        cookie_jar.extract_cookies(
            response=response, request=connection)

        # Handle possible redirects
        location = response.headers.get("Location")
        content_location = response.headers.get("Content-Location")

        # If there is no Location, we will follow Content-Location
        redirect_location = location or content_location

        if redirect_location is not None:
            # https://stackoverflow.com/a/27357138
            utils.requote_uri(
                redirect_location.encode(encoding="latin1").decode(encoding='utf-8')
            )

            if not redirect_location.startswith(("http://", "https://")):
                if redirect_location.startswith("/"):
                    # full path
                    redirect_location = urllib.parse.urlunparse((url.scheme, url.netloc, redirect_location, "", "", ""))
                else:
                    # relative path
                    path = os.path.join(os.path.dirname(url.path), redirect_location)
                    redirect_location = urllib.parse.urlunparse((url.scheme, url.netloc, path, "", "", ""))

            total_redirects += 1

            # Strip tracking fields from the redirect URL
            url = url_cleaner.clear_url(url=redirect_location, **kwargs)

            # Response body is ignored in redirects
            connection.close()

            continue

        if parse_documents:
            content = response.read(
                max_fetch_size if max_fetch_size is not None else config.HTTP_MAX_FETCH_SIZE
            )

            # Close connection after reading response body
            connection.close()

            # Try to decode the response body using utf-8 as encoding
            decoded_content = content.decode(encoding="utf-8")

            for ruleset in body_redirects.iter():
                match_found = None

                if (
                    ruleset.urlPattern is not None and
                    ruleset.urlPattern.compiled.match(url)
                ) or url.netloc in ruleset.domains:
                    for rule in ruleset.rules.iter():
                        results = rule.compiled.search(decoded_content)

                        if isinstance(results, typing.Match):
                            match_found = True
                            break

                    if match_found:
                        url = utils.requote_uri(html.unescape(results.group(1)))
                        total_redirects += 1
                        break

        connection.close()

        break

    return url
