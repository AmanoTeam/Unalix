from .. import config
from . import coreutils


# Default SSL context for HTTPS connections.
SSL_CONTEXT_VERIFIED = coreutils.create_ssl_context(
    cert_file=config.PATH_CA_BUNDLE
)

SSL_CONTEXT_UNVERIFIED = coreutils.create_ssl_context(
    unverified=True,
    cert_file=config.PATH_CA_BUNDLE
)

