from .objects import Dict, List


# Generic patterns
class Pattern(str):
    pass


class Patterns(List):
    pass

# https://docs.clearurls.xyz/1.21.0/specs/rules/#rules
class Rule(Pattern):
    pass

class Rules(Patterns):
    pass

# https://docs.clearurls.xyz/1.21.0/specs/rules/#rawrules
class RawRule(Pattern):
    pass

class RawRules(Patterns):
    pass

# https://docs.clearurls.xyz/1.21.0/specs/rules/#referralmarketing
class ReferralMarketing(Rule):
    pass

class ReferralsMarketing(Rules):
    pass

# https://docs.clearurls.xyz/1.21.0/specs/rules/#exceptions
class Exception(Pattern):
    pass

class Exceptions(Patterns):
    pass

# https://docs.clearurls.xyz/1.21.0/specs/rules/#redirections
class Redirection(Pattern):
    pass

class Redirections(Patterns):
    pass
