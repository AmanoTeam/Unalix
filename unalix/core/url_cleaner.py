import typing
import urllib.parse

from .. import types
from .. import config
from .. import utils

from . import coreutils

rulesets = coreutils.rulesets_from_files(config.PATH_RULESETS)

def clear_url(
    url: typing.Union[str, urllib.parse.ParseResult],
    ignoreReferralMarketing: typing.Optional[bool] = False,
    ignoreRules: typing.Optional[bool] = False,
    ignoreExceptions: typing.Optional[bool] = False,
    ignoreRawRules: typing.Optional[bool] = False,
    ignoreRedirections: typing.Optional[bool] = False,
    skipBlocked: typing.Optional[bool] = False,
    skipLocal: typing.Optional[bool] = False
) -> str:
    """
    This method implements the same specification used in the addon version of ClearURLs (with a few minor exceptions)
    for removing tracking fields and unshortening URLs.

    Parameters:

        url (str):
            A string representing an HTTP URL.

        ignoreReferralMarketing (bool | optional):
            Pass True to instruct Unalix to not remove referral marketing fields from the URL query. Defaults to False.

            This is similar to ClearURLs's "Allow referral marketing" option.

        ignoreRules (bool | optional):
            Pass True to instruct Unalix to not remove tracking fields from the given URL. Defaults to False.

        ignoreExceptions (bool | optional):
            Pass True to instruct Unalix to ignore exceptions for the given URL. Defaults to False.

        ignoreRawRules (bool | optional):
            Pass True to instruct Unalix to ignore raw rules for the given URL. Defaults to False.

        ignoreRedirections (bool | optional):
            Pass True to instruct Unalix to ignore redirection rules for the given URL. Defaults to False.

        skipBlocked (bool | optional):
            Pass True to instruct Unalix to not process rules for blocked URLs. Defaults to False.

            This is similar to ClearURLs "Allow domain blocking" option, but instead of blocking access to the URL,
            we just ignore all rulesets where it's blocked.

        skipLocal (bool | optional):
            Pass True to instruct Unalix to not process rules for local URLs. Defaults to False.

            This is similar to ClearURLs's "Skip URLs on local hosts" option.

    Usage examples:

      Common rules (used to remove tracking fields found in the URL query)
    
            >>> from unalix import clear_url
            >>> 
            >>> url = "https://deezer.com/track/891177062?utm_source=deezer"
            >>> 
            >>> clear_url(url)
            'https://deezer.com/track/891177062'

      Redirection rules (used to extract redirect URLs found in any part of the URL)

            >>> from unalix import clear_url
            >>> 
            >>> url = "https://www.google.com/url?q=https://pypi.org/project/Unalix"
            >>> 
            >>> clear_url(url)
            'https://pypi.org/project/Unalix'

      Raw rules (used to remove tracking elements found in any part of the URL)

            >>> from unalix import clear_url
            >>> 
            >>> url = "https://www.amazon.com/gp/B08CH7RHDP/ref=as_li_ss_tl"
            >>> 
            >>> clear_url(url)
            'https://www.amazon.com/gp/B08CH7RHDP'

      Referral marketing rules (used to remove referral marketing fields found in the URL query)

            >>> from unalix import clear_url
            >>> 
            >>> url = "https://natura.com.br/p/2458?consultoria=promotop"
            >>> 
            >>> clear_url(url)
            'https://natura.com.br/p/2458'
    """

    for ruleset in rulesets.iter():

        if isinstance(url, (types.URL, urllib.parse.ParseResult)):
            url = types.URL(url.geturl())
        else:
            url = types.URL(url)

        if skipLocal and url.islocal():
            return url

        if skipBlocked and ruleset.completeProvider:
            continue

        if ruleset.urlPattern.compiled.match(f"{url.scheme}://{url.netloc}"):
            if not ignoreExceptions:
                exception_matched = None
                for exception in ruleset.exceptions.iter():
                    if exception.compiled.match(url):
                        exception_matched = True
                        break
                if exception_matched:
                    continue

            original_url = url

            if not ignoreRedirections:
                for redirection in ruleset.redirections:
                    url = types.URL(redirection.compiled.sub(r"\g<1>", url))

                    # # https://github.com/ClearURLs/Addon/issues/71
                    url = url.prepend_scheme_if_needed()

                    if url != original_url:
                        return clear_url(
                            url=utils.requote_uri(urllib.parse.unquote(url)),
                            ignoreReferralMarketing=ignoreReferralMarketing,
                            ignoreRules=ignoreRules,
                            ignoreExceptions=ignoreExceptions,
                            ignoreRawRules=ignoreRawRules,
                            ignoreRedirections=ignoreRedirections,
                            skipBlocked=skipBlocked,
                            skipLocal=skipLocal
                        )

            if url.query:
                if not ignoreRules:
                    for rule in ruleset.rules:
                        url.query = rule.compiled.sub(r"\g<1>", url.query)
                if not ignoreReferralMarketing:
                    for referral in ruleset.referralMarketing:
                        url.query = referral.compiled.sub(r"\g<1>", url.query)

            if url.path:
                if not ignoreRawRules:
                    for rawRule in ruleset.rawRules:
                        url.path = rawRule.compiled.sub("", url.path)

        url = url.geturl()

    url = types.URL(url)

    striped_params = []

    for param in url.query.split(sep="&"):
        try:
            key, value = param.split(sep="=")
        except ValueError:
            continue
        else:
            if value:
                striped_params.append(f"{key}={value}")

    url.query = "&".join(striped_params) if striped_params else ""

    return url.geturl()

