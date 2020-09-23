import re
from urllib.parse import unquote, quote

from httpx._models import URL

from unalix.http_clients import client
from unalix.settings import replacements
from unalix.files import rules

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L566
UNRESERVED_SET = frozenset(
	"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789-._~")

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L570
def unquote_unreserved(uri: str) -> str:
	"""Un-escape any percent-escape sequences in a URI that are unreserved
	characters. This leaves all reserved, illegal and non-ASCII bytes encoded.
	"""
	parts = uri.split('%')
	for i in range(1, len(parts)):
		h = parts[i][0:2]
		if len(h) == 2 and h.isalnum():
			c = chr(int(h, 16))
			if c in UNRESERVED_SET:
				parts[i] = c + parts[i][2:]
			else:
				parts[i] = '%' + parts[i]
		else:
			parts[i] = '%' + parts[i]
	return ''.join(parts)

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L594
def requote_uri(uri: str) -> str:
	"""Re-quote the given URI.

	This function passes the given URI through an unquote/quote cycle to
	ensure that it is fully and consistently quoted.
	"""
	safe_with_percent = "!#$%&'()*+,/:;=?@[]~"
	safe_without_percent = "!#$&'()*+,/:;=?@[]~"
	try:
		# Unquote only the unreserved characters
		# Then quote only illegal characters (do not quote reserved,
		# unreserved, or '%')
		return quote(unquote_unreserved(uri), safe=safe_with_percent)
	except ValueError:
		# We couldn't unquote the given URI, so let's try quoting it, but
		# there may be unquoted '%'s in the URI. We need to make sure they're
		# properly quoted so they do not cause issues elsewhere.
		return quote(uri, safe=safe_without_percent)
	
def parse_url(url: str) -> str:
	"""Parse a url
	
	This function will:
	
	* Add the "http://" prefix if the URL provided does not have a defined protocol.
	* Convert domain names in non-Latin alphabet to punycode.
	
	Usage:
	
	  >>> from unalix.utils import parse_url
	  >>> clear_url('i❤️.ws')
	  'http://xn--i-7iq.ws/'
	"""
	# If the specified URL does not have a protocol defined, it will be set to 'http'
	if url.startswith('http://') or url.startswith('https://'):
		url = URL(url)
	else:
		url = URL('http://' + url)
	
	# Encode domain name according to IDNA
	url.copy_with(
		host=url.host.encode('idna').decode('utf-8')
	)
	
	url = str(url)
	
	return url
	
def clear_url(url: str, **kwargs) -> str:
	"""Remove tracking fields from the url
	
	:param url: URL to be processed.
	:param **kwargs: Optional arguments that `parse_rules` takes.
	:return: :class:`str`
	:rtype: str
	
	Usage:
	
	  >>> from unalix.utils import clear_url
	  >>> clear_url('http://g.co/?utm_source=google')
	  'http://g.co/'
	"""
	
	url = parse_url(url)
	url = parse_rules(url, **kwargs)
	
	return url
	
def unshort_url(url: str) -> str:
	"""Try to unshort the given url
	
	Unshortening is done by following 3xx redirects and removing
	tracking fields from the URL before making the request.
	
	The `parse_rules()` function is called for each link
	accessed through the `client.stream()` method.
	
	:param url: URL to be processed.
	:return: :class:`str`
	:rtype: str
	
	Usage:
	
	  >>> from unalix.utils import unshort_url
	  >>> unshort_url('https://bitly.is/Pricing-Pop-Up')
	"""
	url = parse_url(url)
	
	with client.stream('GET', url) as response:
		url = str(response.url)
	
	return url

def parse_rules(
	url: str,
	allow_referral: bool = False,
	ignore_rules: bool = False,
	ignore_exceptions: bool = False,
	ignore_raw: bool = False,
	ignore_redirections: bool = False
) -> str:
	"""Parse regex rules from "data.min.json" and "custom-data.min.json"
	files.
	
	Take a look at https://github.com/ClearURLs/Addon/wiki/Rules to
	understand how these rules are processed.
	
	:param url: URL to be processed.
	:param allow_referral: (optional) If `True`, referral marketing fields
		will not be removed from the URL (if there is any).
	:param ignore_rules: (optional) If `True`, "rules" rules will be ignored.
	:param ignore_exceptions: (optional) If `True`, "exceptions" rules will be ignored.
	:param ignore_raw: (optional) If `True`, "raw" rules will be ignored.
	:param ignore_redirections: (optional) If `True`, "redirections" rules will be ignored.
	:return: :class:`str`
	:rtype: str
	
	Usage:
	
	  >>> from unalix.utils import parse_rules
	  >>> parse_rules('http://g.co/?utm_source=google')
	  'http://g.co/'
	"""
	original_url = url
	skip_provider = False
	
	for rule in rules:
		for provider in rule['providers'].keys():
			if not rule['providers'][provider]['completeProvider']:
				for pattern in [rule['providers'][provider]['urlPattern']]:
					if re.match(pattern, url):
						if not ignore_exceptions:
							for exception in rule['providers'][provider]['exceptions']:
								if re.match(exception, url):
									skip_provider = True
									break
						if not skip_provider:
							if not ignore_redirections:
								for redirection in rule['providers'][provider]['redirections']:
									url = re.sub(rf'{redirection}.*', '\g<1>', url)
								if url != original_url:
									url = unquote(url)
									url = requote_uri(url)
							if not ignore_rules:
								for common in rule['providers'][provider]['rules']:
									url = re.sub(rf'(%26|&|%23|#|%3F|%3f|\?){common}((\=|%3D|%3d)[^&]*)', '\g<1>', url)
							if not allow_referral:
								for referral in rule['providers'][provider]['referralMarketing']:
									url = re.sub(rf'(%26|&|%23|#|%3F|%3f|\?){referral}((\=|%3D|%3d)[^&]*)', '\g<1>', url)
							if not ignore_raw:
								for raw in rule['providers'][provider]['rawRules']:
									url = re.sub(raw, '', url)
							original_url = url
	
	for pattern, replacement in replacements:
		url = re.sub(pattern, replacement, url)
	
	return url
