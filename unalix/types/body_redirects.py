import typing

from .objects import Dict, List
from .patterns import Pattern, Patterns
from .domains import Domains


class BodyRedirect(Dict):


    def __init__(
        self,
        providerName: str,
        urlPattern: typing.Union[Pattern, None],
        domains: Domains,
        rules: Patterns
    ):

        self.providerName = providerName
        self.urlPattern = urlPattern
        self.domains = domains
        self.rules = rules


class BodyRedirects(List):


    def add_ruleset(self, ruleset: BodyRedirect):

        self.base_list.append(ruleset)

