from http.client import HTTPConnection, HTTPSConnection
from typing import List, Tuple, Any, Union
from urllib.parse import ParseResult

# HTTP(S) connection
Connection = Union[HTTPConnection, HTTPSConnection]

# URL
URL = Union[str, ParseResult]

# Compiled regex patterns
CompiledPatterns = Tuple[List[Any], List[Any], List[Any]]

Rules = List[str]
Replacements = List[Tuple[str, str]]
Redirects = List[str]
