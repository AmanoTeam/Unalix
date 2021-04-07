import json
import re
import typing
import ssl
import platform

from ..types.rulesets import Ruleset, Rulesets
from ..types.patterns import Pattern, Patterns
from ..types.domains import Domains
from ..types.body_redirects import BodyRedirect, BodyRedirects


def rulesets_from_files(iterable_of_paths: typing.Iterable) -> Rulesets:

    iterable_of_dicts = []

    for ruleset in iterable_of_paths:
        with open(file=ruleset, mode="r") as file:
            content = file.read()

        iterable_of_dicts.append(json.loads(content))

    rulesets = Rulesets()

    for ruleset in iterable_of_dicts:

        for providerName in ruleset["providers"].keys():

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#urlpattern
            urlPattern = Pattern(ruleset["providers"][providerName]["urlPattern"])
            urlPattern.compiled = re.compile(urlPattern)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#completeprovider
            completeProvider = ruleset["providers"][providerName].get("completeProvider", False)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#rules
            rules = Patterns()
            for rule in ruleset["providers"][providerName].get("rules", []):
                pattern = Pattern(rule)
                pattern.compiled = re.compile(rf"(%(?:26|23)|&|^){rule}(?:(?:=|%3[Dd])[^&]*)")

                rules.append(pattern)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#rawrules
            rawRules = Patterns()
            for rawRule in ruleset["providers"][providerName].get("rawRules", []):
                pattern = Pattern(rawRule)
                pattern.compiled = re.compile(rawRule)

                rawRules.append(pattern)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#referralmarketing
            referralMarketing = Patterns()
            for referral in ruleset["providers"][providerName].get("referralMarketing", []):
                pattern = Pattern(referral)
                pattern.compiled = re.compile(rf"(%(?:26|23)|&|^){referral}(?:(?:=|%3[Dd])[^&]*)")

                referralMarketing.append(pattern)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#exceptions
            exceptions = Patterns()
            for exception in ruleset["providers"][providerName].get("exceptions", []):
                pattern = Pattern(exception)
                pattern.compiled = re.compile(exception)

                exceptions.append(pattern)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#redirections
            redirections = Patterns()
            for redirection in ruleset["providers"][providerName].get("redirections", []):
                pattern = Pattern(redirection)
                pattern.compiled = re.compile(f"{redirection}.*")

                redirections.append(pattern)

            # https://docs.clearurls.xyz/1.21.0/specs/rules/#forceredirection
            # This field is ignored by Unalix, we are leaving it here just as reference
            forceRedirection = ruleset["providers"][providerName].get("forceRedirection", False)

            rulesets.add_ruleset(
                Ruleset(
                    providerName=providerName,
                    urlPattern=urlPattern,
                    completeProvider=completeProvider,
                    rules=rules,
                    rawRules=rawRules,
                    referralMarketing=referralMarketing,
                    exceptions=exceptions,
                    redirections=redirections,
                    forceRedirection=forceRedirection
                )
            )

    return rulesets


def domains_from_files(iterable_of_paths: typing.Iterable) -> Domains:

    domains = Domains()

    for path in iterable_of_paths:
        with open(file=path, mode="r") as file:
            content = file.read()

        for domain in json.loads(content):
            domains.add_domain(domain)

    return domains


def body_redirects_from_files(iterable_of_paths: typing.Iterable) -> BodyRedirects:

    iterable_of_lists = []

    for path in iterable_of_paths:
        with open(file=path, mode="r") as file:
            content = file.read()

        iterable_of_lists.append(json.loads(content))

    body_redirects = BodyRedirects()

    for _ruleset in iterable_of_lists:

        for ruleset in _ruleset:

            providerName = ruleset["providerName"]

            if ruleset["urlPattern"] is None:
                urlPattern = None
            else:
                urlPattern = Pattern(ruleset["urlPattern"])
                urlPattern.compiled = re.compile(urlPattern)

            domains = Domains(ruleset["domains"])

            rules = Patterns()
            for rule in ruleset["rules"]:
                pattern = Pattern(rule)
                pattern.compiled = re.compile(rule)

                rules.append(pattern)

            body_redirects.add_ruleset(
                BodyRedirect(
                    providerName=providerName,
                    urlPattern=urlPattern,
                    domains=domains,
                    rules=rules
                )
            )

    return body_redirects


# https://github.com/encode/httpx/blob/0.16.1/httpx/_config.py#L98
# https://github.com/encode/httpx/blob/0.16.1/httpx/_config.py#L151
def create_ssl_context(
    unverified: typing.Optional[bool] = False,
    cert_file: typing.Optional[str] = None
) -> ssl.SSLContext:
    """
    This function creates the default SSL context for HTTPS connections.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    context.verify_mode = ssl.CERT_NONE if unverified else ssl.CERT_REQUIRED
    context.check_hostname = False if unverified else True

    # Ciphers list for HTTPS connections
    ssl_ciphers = ":".join(
        (
            "ECDHE+AESGCM",
            "ECDHE+CHACHA20",
            "DHE+AESGCM",
            "DHE+CHACHA20",
            "ECDH+AESGCM",
            "DH+AESGCM",
            "ECDH+AES",
            "DH+AES",
            "RSA+AESGCM",
            "RSA+AES",
            "!aNULL",
            "!eNULL",
            "!MD5",
            "!DSS"
        )
    )

    context.set_ciphers(ssl_ciphers)

    # Default options for SSL contexts
    ssl_options = (
        ssl.OP_ALL
        | ssl.OP_NO_COMPRESSION
        | ssl.OP_SINGLE_DH_USE
        | ssl.OP_SINGLE_ECDH_USE
    )

    major, minor, micro = platform.python_version_tuple()
    python_version = float(f"{major}.{minor}")

    # These options are deprecated since Python 3.7
    if python_version == 3.6:
        ssl_options |= (
            ssl.OP_NO_SSLv2
            | ssl.OP_NO_SSLv3
            | ssl.OP_NO_TLSv1
            | ssl.OP_NO_TLSv1_1
            | ssl.OP_NO_TICKET
        )

    context.options = ssl_options

    # Default verify flags for SSL contexts
    ssl_verify_flags = (
        ssl.VERIFY_X509_TRUSTED_FIRST
        | ssl.VERIFY_DEFAULT
    )

    context.verify_flags = ssl_verify_flags

    # CA bundle for server certificate validation
    context.load_verify_locations(cafile=cert_file)

    if ssl.HAS_ALPN:
        context.set_alpn_protocols(["http/1.1"])

    if python_version >= 3.7:
        # Only available in Python 3.7 or higher
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3

        # Disable using 'commonName' for SSLContext.check_hostname
        # when the 'subjectAltName' extension isn't available.
        try:
            # Only writable in OpenSSL v1.1.0+
            context.hostname_checks_common_name = False
        except AttributeError:
            pass

    if python_version >= 3.8:
        # Signal to server support for PHA in TLS 1.3.
        try:
            # Only writable in OpenSSL v1.1.1+ with TLS 1.3 support.
            context.post_handshake_auth = True
        except AttributeError:
            pass

    return context
