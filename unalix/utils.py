import re
from urllib.parse import unquote, quote

import idna
import rfc3986

from unalix.http_clients import client
from unalix.settings import rules, replacements

UNRESERVED_SET = frozenset(
	"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789-._~")

def unquote_unreserved(uri):
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

def requote_uri(uri):
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
	
def clear_url(url, unshort=True):
	"""Clear and unshort the :url:
	
	Usage:
	
	  >>> from unalix import clear_url
	  >>> clear_url('http://g.co/?utm_source=google')
	  'https://g.co/'
	"""
	# If the specified URL does not have a protocol defined, it will be set to 'http'
	if url.startswith('http://') or url.startswith('https://'):
		url = rfc3986.urlparse(url)
	else:
		url = rfc3986.urlparse(f'http://{url}')
	
	# If the specified URL has a domain name in non-Latin alphabet, encode it according to IDNA
	try:
		idna.encode(url.host, strict=True, std3_rules=True)
	except idna.core.InvalidCodepoint:
		url = url.copy_with(host=url.host.encode('idna'))
	
	url = url.geturl()
	url = parse_regex_rules(url)
	
	if unshort:
		with client.stream('GET', url) as response:
			url = str(response.url)
	
	return url
	
def parse_regex_rules(url):
	"""Process regex rules from rules/*.json
	
	Usage:
	
	  >>> from unalix import parse_regex_rules
	  >>> parse_regex_rules('http://g.co/?utm_source=google')
	  'http://g.co/'
	"""
	original_url = url
	skip_provider = False
	
	for rule in rules:
		for provider in rule['providers'].keys():
			if not rule['providers'][provider]['completeProvider']:
				for pattern in [rule['providers'][provider]['urlPattern']]:
					if re.match(pattern, url):
						for exception in rule['providers'][provider]['exceptions']:
							if re.match(exception, url):
								skip_provider = True
								break
						if not skip_provider:
							for redirection in rule['providers'][provider]['redirections']:
								url = re.sub(rf'{redirection}.*', '\g<1>', url)
							if url != original_url:
								url = unquote(url)
								url = requote_uri(url)
							for common in rule['providers'][provider]['rules']:
								url = re.sub(rf'(%26|&|%23|#|%3F|%3f|\?){common}(\=[^&]*)', '\g<1>', url)
							for referral in rule['providers'][provider]['referralMarketing']:
								url = re.sub(rf'(%26|&|%23|#|%3F|%3f|\?){referral}(\=[^&]*)', '\g<1>', url)
							for raw in rule['providers'][provider]['rawRules']:
								url = re.sub(raw, '', url)
							original_url = url
	
	for pattern, replacement in replacements:
		url = re.sub(pattern, replacement, url)
	
	return url
