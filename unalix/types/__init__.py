from .objects import Object, Dict, List
from .patterns import (
    Pattern,
    Patterns,
    Rule,
    Rules,
    RawRule,
    RawRules,
    ReferralMarketing,
    ReferralsMarketing,
    Exception,
    Exceptions,
    Redirection,
    Redirections
)
from .rulesets import Ruleset, Rulesets
from .body_redirects import BodyRedirect, BodyRedirects
from .domains import Domains
from .urls import URL, URL_TYPES


__all__ = [
    "Object",
    "Dict",
    "List",
    "Pattern",
    "Patterns",
    "Ruleset",
    "Rulesets",
    "Rule",
    "Rules",
    "RawRule",
    "RawRules",
    "ReferralMarketing",
    "ReferralsMarketing",
    "Exception",
    "Exceptions",
    "Redirection",
    "Redirections",
    "BodyRedirect",
    "BodyRedirects",
    "Domains",
    "URL",
    "URL_TYPES"
]

__locals = locals()

for __name in __all__:
    try:
        setattr(__locals[__name], "__module__", "unalix.types")
    except AttributeError:
        pass
