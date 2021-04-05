from .objects import Object, Dict, List
from .patterns import Pattern, Patterns
from .rulesets import Ruleset, Rulesets
from .body_redirects import BodyRedirect, BodyRedirects
from .domains import Domains
from .urls import URL
from .paths import Path
from .tuples import Tuple
from .ints import Int
from .dicts import Dict


__all__ = [
    "Object",
    "Dict",
    "List",
    "Pattern",
    "Patterns",
    "Ruleset",
    "Rulesets",
    "BodyRedirect",
    "BodyRedirects",
    "Domains",
    "URL",
    "Path",
    "Tuple",
    "Int",
    "Dict"
]

__locals = locals()

for __name in __all__:
    setattr(__locals[__name], "__module__", "unalix.types")
