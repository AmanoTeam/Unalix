from .objects import Dict, List
from .patterns import Pattern, Patterns


class Ruleset(Dict):


    def __init__(
        self,
        providerName: str,
        urlPattern: Pattern,
        completeProvider: bool,
        rules: Patterns,
        rawRules: Patterns,
        referralMarketing: Patterns,
        exceptions: Patterns,
        redirections: Patterns,
        forceRedirection: bool
    ):
        self.providerName = providerName
        self.urlPattern = urlPattern
        self.completeProvider = completeProvider
        self.rules = rules
        self.rawRules = rawRules
        self.referralMarketing = referralMarketing
        self.exceptions = exceptions
        self.redirections = redirections
        self.forceRedirection = forceRedirection


class Rulesets(List):


    def add_ruleset(self, ruleset: Ruleset):

        self._list.append(ruleset)

