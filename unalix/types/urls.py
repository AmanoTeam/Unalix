import urllib.parse
import ipaddress


class URL(str):


    def __init__(self, url):

        self.url = url

        (
            self.scheme, self.netloc, self.path,
            self.params, self.query, self.fragment
        ) = urllib.parse.urlparse(url)

        self.port = None

        parts = self.netloc.split(sep=":")

        if len(parts) > 1:
            part = parts[-1]
            if part.isnumeric():
                self.port = int(part)

        if self.port is None:
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443


    def islocal(self) -> bool:

        local_domains = (
            "localhost",
            "localhost.localdomain",
            "ip6-localhost",
            "ip6-loopback"
        )

        try:
            address = ipaddress.ip_address(self.netloc)
        except ValueError:
            return True if self.netloc in local_domains else False
        else:
            return True if address.is_private else False


    def geturl(self):

        return urllib.parse.urlunparse((
            self.scheme, self.netloc, self.path,
            self.params, self.query, self.fragment
        ))


    # https://github.com/psf/requests/blob/2c2138e811487b13020eb331482fb991fd399d4e/requests/utils.py#L903
    def prepend_scheme_if_needed(self):

        (
            scheme, netloc, path,
            params, query, fragment
        ) = urllib.parse.urlparse(self.geturl(), "http")

        if not netloc:
            netloc, path = path, netloc

        return URL(
            urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))
        )

