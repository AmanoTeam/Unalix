import asyncio
import typing
import http
import http.cookiejar
import http.client
import ssl
import html
import urllib.parse
import time
import datetime
import os

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
    method: typing.Optional[str] = None,
    parse_documents: typing.Optional[bool] = False,
    max_redirects: typing.Optional[int] = None,
    timeout: typing.Optional[int] = None,
    headers: typing.Optional[typing.Dict[str, str]] = None,
    max_fetch_size: typing.Optional[int] = None,
    cookies: typing.Optional[http.cookiejar.CookieJar] = None,
    cookies_policy: typing.Optional[http.cookiejar.DefaultCookiePolicy] = None,
    context: typing.Optional[ssl.SSLContext] = None,
    max_retries:  typing.Optional[int] = None,
    status_retry:  typing.Optional[typing.Iterable[typing.Union[int, http.HTTPStatus]]] = None,
    **kwargs: typing.Any
):
    """
    This method implements a simple HTTP 1.1 client, mainly used to follow HTTP redirects and read responses body.
    We ensure that all redirect URLs are cleaned before following them.

    Parameters:

        url (str):
            A valid RFC 3986 HTTP URI.

        method (str):
            A valid RFC 7231 HTTP method. Defaults to unalix.config.HTTP_METHOD.

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
            HTTP request headers as {"key": "value"} pairs. Defaults to unalix.config.HTTP_HEADERS.

        max_fetch_size (int | optional):
            Max number of bytes to fetch from response body. Only takes effect when parse_documents is set to True, as Unalix igores response body by default.
            Defaults to unalix.config.HTTP_MAX_FETCH_SIZE.

        cookies (http.cookiejar.CookieJar | optional):
            Custom CookieJar object.

        cookies_policy (http.cookiejar.DefaultCookiePolicy | optional):
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
            List or iterable of HTTP status code to retry on. Defaults to unalix.config.HTTP_STATUS_RETRY.

            Only takes effect when max_retries > 0.

        **kwargs (optional):
            Optional keyword arguments that unalix.clear_url() takes.

    Usage examples:

        Rejecting all cookies

            >>> import unalix
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> unalix.unshort_url(url, cookies_policy=unalix.COOKIE_REJECT_ALL)
            'https://bitly.com/pages/pricing'

      Allowing all cookies

            >>> import unalix
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> unalix.unshort_url(url, cookies_policy=unalix.COOKIE_ALLOW_ALL)
            'https://bitly.com/pages/pricing'

      Disabling SSL certificate validation

            >>> import unalix
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> unalix.unshort_url(url, context=unalix.SSL_CONTEXT_UNVERIFIED)
            'https://bitly.com/pages/pricing'
    """

    # Cookies
    cookie_jar = (
        cookies if cookies is not None else http.cookiejar.CookieJar()
    )
    cookie_jar.set_policy(
        cookies_policy if cookies_policy is not None else cookie_policies.COOKIE_STRICT_ALLOW
    )

    total_redirects = 0
    total_retries = 0

    # HTTP options
    (
        http_method,
        http_timeout,
        http_max_redirects,
        http_max_retries,
        http_headers,
        http_status_retry,
        http_max_fetch
    ) = (
        method if method is not None else config.HTTP_METHOD,
        timeout if timeout is not None else config.HTTP_TIMEOUT,
        max_redirects if max_redirects is not None else config.HTTP_MAX_REDIRECTS,
        max_retries if max_retries is not None else config.HTTP_MAX_RETRIES,
        headers if headers is not None else config.HTTP_HEADERS,
        status_retry if status_retry is not None else config.HTTP_STATUS_RETRY,
        max_fetch_size if max_fetch_size is not None else config.HTTP_MAX_FETCH_SIZE
    )

    # SSL context for HTTPS requests
    tls_context = (
        context if context is not None else ssl_context.SSL_CONTEXT_VERIFIED
    )

    while True:

        if isinstance(url, types.URL_TYPES):
            url = types.URL(url.geturl())
        else:
            url = types.URL(url)

        if url.scheme == "http":
            connection = http.client.HTTPConnection(
                host=url.netloc,
                port=url.port,
                timeout=http_timeout
            )
        elif url.scheme == "https":
            connection = http.client.HTTPSConnection(
                host=url.netloc,
                port=url.port,
                timeout=http_timeout,
                context=tls_context
            )
        else:
            raise exceptions.UnsupportedProtocolError(
                message="Unrecognized URI or unsupported protocol",
                url=url
            ) from None

        # Workaround for making http.client's connection objects compatible with
        # CookieJar's extract_cookies() and add_cookie_header() methods.

        # https://docs.python.org/3/library/urllib.request.html#urllib.request.Request.unverifiable
        connection.unverifiable = True

        # https://docs.python.org/3/library/urllib.request.html#urllib.request.Request.has_header
        connection.has_header = lambda header_name: False
        
        # https://docs.python.org/3/library/urllib.request.html#urllib.request.Request.get_full_url
        connection.get_full_url = lambda: str(url)

        # https://docs.python.org/3/library/urllib.request.html#urllib.request.Request.origin_req_host
        connection.origin_req_host = url.netloc

        connection.headers = {}
        connection.cookies = {}

        # https://docs.python.org/3/library/urllib.request.html#urllib.request.Request.add_unredirected_header
        add_unredirected_header = lambda key, value: connection.headers.update({key: value})
        connection.add_unredirected_header = add_unredirected_header

        cookie_jar.add_cookie_header(connection)

        # Merge headers added by cookie_jar.add_cookie_header() with default headers
        connection_headers = dict(http_headers)
        connection_headers.update(connection.headers)

        uri = f"{url.path}?{url.query}" if url.query else url.path

        try:
            connection.request(
                method=http_method,
                url=uri,
                headers=connection_headers
            )
            response = connection.getresponse()
        except Exception as exception:
            connection.close()
            
            # Retry based on connection error
            if http_max_retries > 0:
                total_retries += 1

                if total_retries > http_max_retries:
                    raise exceptions.MaxRetriesError(
                        message="Exceeded maximum allowed retries",
                        url=url
                    ) from exception

                continue

            raise exceptions.ConnectError(
                message="Connection error",
                url=url
            ) from exception
        else:
            # Retry based on status code
            if http_max_retries > 0 and response.code in http_status_retry:
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None:
                    if retry_after.isnumeric():
                        time.sleep(int(retry_after))
                    else:
                        http_date = datetime.datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S GMT")
                        time.sleep(int(http_date.timestamp()) - int(time.time()))
                
                total_retries += 1
                
                if total_retries > http_max_retries:
                    raise exceptions.MaxRetriesError(
                        message="Exceeded maximum allowed retries",
                        url=url
                    ) from None

                continue

        # Extract cookies from response
        cookie_jar.extract_cookies(
            response=response, request=connection)

        if response.status in config.http.HTTP_STATUS_REDIRECT:
            # Handle HTTP redirects
            redirect_location = response.headers.get("Location")
            assert redirect_location is not None
        else:
            # If there is no "Location", we will look for "Content-Location"
            redirect_location = response.headers.get("Content-Location")

        if redirect_location is not None:
            # https://stackoverflow.com/a/27357138
            utils.requote_uri(
                redirect_location.encode(encoding="latin1").decode(encoding='utf-8')
            )

            if not redirect_location.startswith(("http://", "https://")):
                if redirect_location.startswith("//"):
                    # new url
                    redirect_location = urllib.parse.urlunparse((url.scheme, redirect_location.lstrip("/"), "", "", "", ""))
                elif redirect_location.startswith("/"):
                    # full path
                    redirect_location = urllib.parse.urlunparse((url.scheme, (url.netloc if url.port in (80, 443) else f"{url.netloc}:{url.port}") , redirect_location, "", "", ""))
                else:
                    # relative path
                    path = os.path.join(os.path.dirname(url.path), redirect_location)
                    redirect_location = urllib.parse.urlunparse((url.scheme, (url.netloc if url.port in (80, 443) else f"{url.netloc}:{url.port}"), path, "", "", ""))

            # Avoid redirect loops
            if redirect_location == url:
                return url

            total_redirects += 1

            # Strip tracking fields from the redirect URL
            url = url_cleaner.clear_url(url=redirect_location, **kwargs)

            # Response body is ignored in redirects
            connection.close()

            if total_redirects > http_max_redirects:
                raise exceptions.TooManyRedirectsError(
                    message="Exceeded maximum allowed redirects",
                    url=url
                ) from None

            continue

        if parse_documents and http_method != "HEAD":
            content = response.read(max_fetch_size)

            # Close connection after reading response body
            connection.close()

            # Get encoding from Content-Type header
            encoding = utils.get_encoding_from_headers(response.headers)

            # Try to decode the response body using the value returned by "get_encoding_from_headers" or "utf-8" as encoding
            decoded_content = content.decode(encoding=(encoding or "utf-8"), errors="ignore")

            for ruleset in body_redirects.iter():

                if (ruleset.urlPattern is not None and ruleset.urlPattern.compiled.match(url) or url.netloc in ruleset.domains):
                    for rule in ruleset.rules.iter():
                        results = rule.compiled.search(decoded_content)
                        if isinstance(results, typing.Match):
                            break
                    else:
                        continue

                    # Strip tracking fields from the extracted URL
                    url = url_cleaner.clear_url(url=utils.requote_uri(html.unescape(results.group(1))), **kwargs)

                    total_redirects += 1

                    if total_redirects > http_max_redirects:
                        raise exceptions.TooManyRedirectsError(
                            message="Exceeded maximum allowed redirects",
                            url=url
                        ) from None

                    break
            else:
                return url
            
            continue
        else:
            connection.close()

        return url


async def aunshort_url(
    url: typing.Union[str, urllib.parse.ParseResult],
    method: typing.Optional[str] = None,
    parse_documents: typing.Optional[bool] = False,
    max_redirects: typing.Optional[int] = None,
    timeout: typing.Optional[int] = None,
    ssl_handshake_timeout: typing.Optional[int] = None,
    headers: typing.Optional[typing.Dict[str, str]] = None,
    max_fetch_size: typing.Optional[int] = None,
    context: typing.Optional[ssl.SSLContext] = None,
    max_retries:  typing.Optional[int] = None,
    status_retry:  typing.Optional[typing.Iterable[typing.Union[int, http.HTTPStatus]]] = None,
    **kwargs: typing.Any
):
    """
    This method implements a simple HTTP 1.1 client, mainly used to follow HTTP redirects and read responses body.
    We ensure that all redirect URLs are cleaned before following them.

    Parameters:

        url (str):
            A valid RFC 3986 HTTP URI.

        method (str):
            A valid RFC 7231 HTTP method. Defaults to unalix.config.HTTP_METHOD.

        parse_documents (bool | optional):
            Pass True to instruct Unalix to look for redirect URLs in the response body when there is no HTTP redirect
            to follow. Defaults to False.

            This method is unstable and sometimes can return broken or incomplete URLs. Use with caution.

        max_redirects (int | optional):
            Max number of HTTP redirects to follow before raising an exception. Defaults to unalix.config.HTTP_MAX_REDIRECTS.

            Redirects followed from the response body also counts.

        timeout (int | optional):
            Max number of seconds to wait for a response before raising an exception. Defaults to unalix.config.HTTP_TIMEOUT.

        ssl_handshake_timeout (int | optional):
            Max number of seconds to wait for the ssl handshake before raising an exception. Defaults to unalix.config.HTTP_TIMEOUT.

        headers (dict | optional):
            HTTP request headers as {"key": "value"} pairs. Defaults to unalix.config.HTTP_HEADERS.

        max_fetch_size (int | optional):
            Max number of bytes to fetch from response body. Only takes effect when parse_documents is set to True, as Unalix igores response body by default.
            Defaults to unalix.config.HTTP_MAX_FETCH_SIZE.

        context (ssl.SSLContext | optional):
            Custom SSL context for HTTPS connections. Defaults to unalix.SSL_CONTEXT_VERIFIED.

        max_retries (int | optional):
            Max number of times to retry on connection errors. Defaults to unalix.config.HTTP_MAX_RETRIES.

        status_retry (typing.Iterable | optional):
            List or iterable of HTTP status code to retry on. Defaults to unalix.config.HTTP_STATUS_RETRY.

            Only takes effect when max_retries > 0.

        **kwargs (optional):
            Optional keyword arguments that unalix.clear_url() takes.

    Usage examples:

        Rejecting all cookies

            >>> import asyncio
            >>> 
            >>> import unalix
            >>> 
            >>> loop = asyncio.get_event_loop()
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> loop.run_until_complete(unalix.aunshort_url(url, cookies_policy=unalix.COOKIE_REJECT_ALL))
            'https://bitly.com/pages/pricing'

      Allowing all cookies

            >>> import asyncio
            >>> 
            >>> import unalix
            >>> 
            >>> loop = asyncio.get_event_loop()
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> loop.run_until_complete(unalix.aunshort_url(url, cookies_policy=unalix.COOKIE_ALLOW_ALL))
            'https://bitly.com/pages/pricing'

      Disabling SSL certificate validation

            >>> import asyncio
            >>> 
            >>> import unalix
            >>> 
            >>> loop = asyncio.get_event_loop()
            >>> 
            >>> url = "https://bitly.is/Pricing-Pop-Up'
            >>> 
            >>> loop.run_until_complete(unalix.aunshort_url(url, context=unalix.SSL_CONTEXT_UNVERIFIED))
            'https://bitly.com/pages/pricing'
    """

    total_redirects = 0
    total_retries = 0

    # HTTP options
    (
        http_method,
        http_timeout,
        ssl_handshake_timeout,
        http_max_redirects,
        http_max_retries,
        http_headers,
        http_status_retry,
        http_max_fetch
    ) = (
        method if method is not None else config.HTTP_METHOD,
        timeout if timeout is not None else config.HTTP_TIMEOUT,
        ssl_handshake_timeout if ssl_handshake_timeout is not None else config.HTTP_TIMEOUT,
        max_redirects if max_redirects is not None else config.HTTP_MAX_REDIRECTS,
        max_retries if max_retries is not None else config.HTTP_MAX_RETRIES,
        headers if headers is not None else config.HTTP_HEADERS,
        status_retry if status_retry is not None else config.HTTP_STATUS_RETRY,
        max_fetch_size if max_fetch_size is not None else config.HTTP_MAX_FETCH_SIZE
    )

    # SSL context for HTTPS requests
    tls_context = (
        context if context is not None else ssl_context.SSL_CONTEXT_VERIFIED
    )

    parse_documents = (
        parse_documents and http_method != "HEAD"
    )

    while True:

        if isinstance(url, types.URL_TYPES):
            url = types.URL(url.geturl())
        else:
            url = types.URL(url)

        if url.scheme == "http":
            future = asyncio.open_connection(
                host=url.netloc,
                port=url.port
            )
        elif url.scheme == "https":
            future = asyncio.open_connection(
                host=url.netloc,
                port=url.port,
                ssl=tls_context,
                ssl_handshake_timeout=ssl_handshake_timeout
            )
        else:
            raise exceptions.UnsupportedProtocolError(
                message="Unrecognized URI or unsupported protocol",
                url=url
            ) from None

        reader, writer = None, None

        try:
            reader, writer = await asyncio.wait_for(fut=future, timeout=http_timeout)

            raw_request = (
                f"{http_method} {f'{url.path}?{url.query}' if url.query else (url.path if url.path else '/')} HTTP/1.0\n" +
                f"Host: {url.netloc}\n"
            )

            for key, value in http_headers.items():
                raw_request += f"{key}: {value}\n"
            raw_request += "\n"

            writer.write(
                data=raw_request.encode(encoding="latin-1")
            )

            if parse_documents:
                received_data = await asyncio.wait_for(
                    fut=reader.read(n=http_max_fetch),
                    timeout=http_timeout
                )

                parts = received_data.decode(encoding="latin-1").split(sep="\r\n\r\n", maxsplit=1)

                if len(parts) < 2:
                    headers, body = parts[0], ""
                else:
                    headers, body = parts
            else:
                received_data = await asyncio.wait_for(
                    fut=reader.readuntil(separator=b"\r\n\r\n"),
                    timeout=http_timeout
                )

                headers, body = received_data.decode(encoding="latin-1").strip(), ""

            headers_d = {}

            for index, header in enumerate(headers.split(sep="\r\n")):
                if index == 0:
                    http_version, status_code, status_message = header.split(sep=" ", maxsplit=2)
                    continue
                key, value = header.split(sep=": ", maxsplit=1)
                headers_d[key] = value

            response = types.Response(
                http_version=float(http_version.split(sep="/")[1]),
                status_code=int(status_code),
                status_message=status_message,
                headers=headers_d,
                body=body
            )
        except Exception as exception:
            if writer is not None:
                writer.close()

            # Retry based on connection error
            if http_max_retries > 0:
                total_retries += 1

                if total_retries > http_max_retries:
                    raise exceptions.MaxRetriesError(
                        message="Exceeded maximum allowed retries",
                        url=url
                    ) from exception

                continue

            raise exceptions.ConnectError(
                message="Connection error",
                url=url
            ) from exception
        else:
            # Retry based on status code
            if http_max_retries > 0 and response.status_code in http_status_retry:
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None:
                    if retry_after.isnumeric():
                        await asyncio.sleep(int(retry_after))
                    else:
                        http_date = datetime.datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S GMT")
                        await asyncio.sleep(int(http_date.timestamp()) - int(time.time()))

                total_retries += 1

                if total_retries > http_max_retries:
                    raise exceptions.MaxRetriesError(
                        message="Exceeded maximum allowed retries",
                        url=url
                    ) from None

                continue

        if response.status_code in config.http.HTTP_STATUS_REDIRECT:
            # Handle HTTP redirects
            redirect_location = response.headers.get("Location") or response.headers.get("location")
            assert redirect_location is not None
        else:
            # If there is no "Location", we will look for "Content-Location"
            redirect_location = response.headers.get("Content-Location") or response.headers.get("content-location")

        if redirect_location is not None:
            # https://stackoverflow.com/a/27357138
            utils.requote_uri(
                redirect_location.encode(encoding="latin1").decode(encoding='utf-8')
            )

            if not redirect_location.startswith(("http://", "https://")):
                if redirect_location.startswith("//"):
                    # new url
                    redirect_location = urllib.parse.urlunparse((url.scheme, redirect_location.lstrip("/"), "", "", "", ""))
                elif redirect_location.startswith("/"):
                    # full path
                    redirect_location = urllib.parse.urlunparse((url.scheme, (url.netloc if url.port in (80, 443) else f"{url.netloc}:{url.port}") , redirect_location, "", "", ""))
                else:
                    # relative path
                    path = os.path.join(os.path.dirname(url.path), redirect_location)
                    redirect_location = urllib.parse.urlunparse((url.scheme, (url.netloc if url.port in (80, 443) else f"{url.netloc}:{url.port}"), path, "", "", ""))

            # Avoid redirect loops
            if redirect_location == url:
                return url

            total_redirects += 1

            # Strip tracking fields from the redirect URL
            url = url_cleaner.clear_url(url=redirect_location, **kwargs)

            if total_redirects > http_max_redirects:
                raise exceptions.TooManyRedirectsError(
                    message="Exceeded maximum allowed redirects",
                    url=url
                ) from None

            continue

        if parse_documents:
            for ruleset in body_redirects.iter():

                if (ruleset.urlPattern is not None and ruleset.urlPattern.compiled.match(url) or url.netloc in ruleset.domains):
                    for rule in ruleset.rules.iter():
                        results = rule.compiled.search(response.body)
                        if isinstance(results, typing.Match):
                            break
                    else:
                        continue

                    # Strip tracking fields from the extracted URL
                    url = url_cleaner.clear_url(url=utils.requote_uri(html.unescape(results.group(1))), **kwargs)

                    total_redirects += 1

                    if total_redirects > http_max_redirects:
                        raise exceptions.TooManyRedirectsError(
                            message="Exceeded maximum allowed redirects",
                            url=url
                        ) from None

                    break
            else:
                return url
            
            continue
        
        return url
