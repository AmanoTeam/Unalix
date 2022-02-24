import typing
import urllib.parse

from .. import types
from .. import config
from .. import utils

from . import coreutils

# Build rulesets object
rulesets = coreutils.rulesets_from_files(
    config.PATH_RULESETS,
    ignored_providers=config.IGNORED_PROVIDERS
)

def clear_url(
    url: typing.Union[str, urllib.parse.ParseResult],
    ignoreReferralMarketing: typing.Optional[bool] = False,
    ignoreRules: typing.Optional[bool] = False,
    ignoreExceptions: typing.Optional[bool] = False,
    ignoreRawRules: typing.Optional[bool] = False,
    ignoreRedirections: typing.Optional[bool] = False,
    skipBlocked: typing.Optional[bool] = False,
    skipLocal: typing.Optional[bool] = False,
    stripDuplicates: typing.Optional[bool] = False,
    stripEmpty: typing.Optional[bool] = False
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

        stripDuplicates (bool | optional):
            Pass True to instruct Unalix to strip fields with duplicate names. Defaults to False.

        stripEmpty (bool | optional):
            Pass True to instruct Unalix to strip fields with empty values. Defaults to False.

    Usage examples:

      Common rules (used to remove tracking fields found in the URL query)
    
            >>> import unalix
            >>> 
            >>> url = "https://deezer.com/track/891177062?utm_source=deezer"
            >>> 
            >>> unalix.clear_url(url)
            'https://deezer.com/track/891177062'

      Redirection rules (used to extract redirect URLs found in any part of the URL)

            >>> import unalix
            >>> 
            >>> url = "https://www.google.com/url?q=https://pypi.org/project/Unalix"
            >>> 
            >>> unalix.clear_url(url)
            'https://pypi.org/project/Unalix'

      Raw rules (used to remove tracking elements found in any part of the URL)

            >>> import unalix
            >>> 
            >>> url = "https://www.amazon.com/gp/B08CH7RHDP/ref=as_li_ss_tl"
            >>> 
            >>> unalix.clear_url(url)
            'https://www.amazon.com/gp/B08CH7RHDP'

      Referral marketing rules (used to remove referral marketing fields found in the URL query)

            >>> import unalix
            >>> 
            >>> url = "https://natura.com.br/p/2458?consultoria=promotop"
            >>> 
            >>> unalix.clear_url(url)
            'https://natura.com.br/p/2458'
    """

    for ruleset in rulesets.iter():

        if isinstance(url, types.URL_TYPES):
            url = types.URL(url.geturl())
        else:
            url = types.URL(url)

        if skipLocal and url.islocal():
            return url

        if skipBlocked and ruleset.completeProvider:
            continue

        # https://docs.clearurls.xyz/latest/specs/rules/#urlpattern
        if ruleset.urlPattern.compiled.match(f"{url.scheme}://{url.netloc}"):
            if not ignoreExceptions:
                exception_matched = None
                # https://docs.clearurls.xyz/latest/specs/rules/#exceptions
                for exception in ruleset.exceptions.iter():
                    if exception.compiled.match(url):
                        exception_matched = True
                        break
                if exception_matched:
                    continue

            if not ignoreRedirections:
                # https://docs.clearurls.xyz/latest/specs/rules/#redirections
                for redirection in ruleset.redirections:
                    result = redirection.compiled.sub(r"\g<1>", url)

                    # Skip empty URLs
                    if not result:
                        continue

                    if result == url:
                        continue

                    url = types.URL(utils.requote_uri(urllib.parse.unquote(result)))

                    # Workaround for URLs without scheme (see https://github.com/ClearURLs/Addon/issues/71)
                    url = url.prepend_scheme_if_needed()

                    return clear_url(
                        url=url,
                        ignoreReferralMarketing=ignoreReferralMarketing,
                        ignoreRules=ignoreRules,
                        ignoreExceptions=ignoreExceptions,
                        ignoreRawRules=ignoreRawRules,
                        ignoreRedirections=ignoreRedirections,
                        skipBlocked=skipBlocked,
                        skipLocal=skipLocal,
                        stripDuplicates=stripDuplicates,
                        stripEmpty=stripEmpty
                    )

            if url.query:
                if not ignoreRules:
                    # https://docs.clearurls.xyz/latest/specs/rules/#rules
                    for rule in ruleset.rules:
                        url.query = rule.compiled.sub(r"\g<1>", url.query)
                if not ignoreReferralMarketing:
                    # https://docs.clearurls.xyz/latest/specs/rules/#referralmarketing
                    for referral in ruleset.referralMarketing:
                        url.query = referral.compiled.sub(r"\g<1>", url.query)

            # The fragment might contains tracking fields as well
            if url.fragment:
                if not ignoreRules:
                    for rule in ruleset.rules:
                        url.fragment = rule.compiled.sub(r"\g<1>", url.fragment)
                if not ignoreReferralMarketing:
                    for referral in ruleset.referralMarketing:
                        url.fragment = referral.compiled.sub(r"\g<1>", url.fragment)

            if url.path:
                if not ignoreRawRules:
                    # https://docs.clearurls.xyz/latest/specs/rules/#rawrules
                    for rawRule in ruleset.rawRules:
                        url.path = rawRule.compiled.sub("", url.path)

        url = url.geturl()

    url = types.URL(url)

    if url.query:
        url.query = utils.filter_query(
            query=url.query,
            stripEmpty=stripEmpty,
            stripDuplicates=stripDuplicates
        )
    
    if url.fragment:
        url.fragment = utils.filter_query(
            query=url.fragment,
            stripEmpty=stripEmpty,
            stripDuplicates=stripDuplicates
        )
    
    return url.geturl()

