import http
import json
import os
import re
import requests
import urllib
import urllib3
import random

# https://docs.python.org/3/library/http.cookiejar.html#defaultcookiepolicy-objects
def CookiePolicy(self, cookie, request):
	return False

http.cookiejar.DefaultCookiePolicy.set_ok = http.cookiejar.DefaultCookiePolicy.return_ok = CookiePolicy

# https://www.whatismybrowser.com/guides/the-latest-user-agent/
user_agents = [
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:76.0) Gecko/20100101 Firefox/76.0',
	'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
	'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edge/44.18363.8131'
	'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 OPR/68.0.3618.125',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 OPR/68.0.3618.125',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 OPR/68.0.3618.125',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Vivaldi/3.0',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Vivaldi/3.0',
	'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Vivaldi/3.0',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 YaBrowser/20.4.0 Yowser/2.5 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 YaBrowser/20.4.0 Yowser/2.5 Safari/537.36',
]

# https://github.com/soimort/translate-shell/wiki/Languages
languages = [
	'af', 'am', 'ar', 'az', 'ba', 'be', 'bg', 'ca', 'ceb', 'co', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fj', 'fr', 'fy', 'ga', 'gd', 'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hmn', 'hr', 'ht', 'hu', 'hy', 'id', 'ig', 'is', 'it', 'ja', 'jv', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mhr', 'mi', 'mk', 'ml', 'mn', 'mr', 'mrj', 'ms', 'mt', 'mww', 'my', 'ne', 'nl', 'no', 'ny', 'otq', 'pa', 'pap', 'pl', 'ps', 'pt', 'ro', 'ru', 'sd', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr-Cyrl', 'sr-Latn', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tl', 'tlh', 'tlh-Qaak', 'to', 'tr', 'tt', 'ty', 'udm', 'uk', 'ur', 'uz', 'vi', 'yo', 'yua', 'yue', 'zh-CN', 'zh-TW', 'zu'
]

# Session for DNS-over-HTTPS requests
doh = requests.Session()

doh.headers = {
	'Accept': 'application/dns-json',
	'Accept-Encoding': None,
	'Connection': None,
	'User-Agent': None
}

# Session for general requests
req = requests.Session()

req.headers = {
	'Accept': '*/*',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': random.choice(languages),
	'Connection': 'keep-alive',
	'User-Agent': random.choice(user_agents)
}

rules_dir = os.path.dirname(__file__) + '/rules/'

ipv4 = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
url_schema = re.compile('^[a-z]+://')
dot_from_host = re.compile('\.$')

# https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small/41041028#41041028
urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
	urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except:
	pass

 # https://stackoverflow.com/questions/22609385/python-requests-library-define-specific-dns/22614367#22614367
def patched_create_connection(address, *args, **kwargs):
	host, port = address
	hostname = resolve(host)
	
	return _orig_create_connection((hostname, port), *args, **kwargs)

_orig_create_connection = urllib3.util.connection.create_connection
urllib3.util.connection.create_connection = patched_create_connection

def resolve(host):
	"""Resolve domain names using DNS-over-HTTPS.
	
	All domain name resolutions will be sent to the server 'fi.doh.dns.snopyta.org' via HTTP.
	
	This method is more secure than the conventional domain name resolution.
	
	Usage:
	
	  >>> from unalix import resolve
	  >>> resolve('python.org')
	  '45.55.99.72'
	"""
	
	if ipv4.match(host):
		return host
	elif host == 'fi.doh.dns.snopyta.org':
		return '95.216.229.153'
	
	params = {
		'name': host,
		'type': 'A'
	}
	
	with doh.get('https://fi.doh.dns.snopyta.org/dns-query', params=params) as request:
		request.raise_for_status()
	
	dns_answer = request.json()['Answer'][0]['data']
	
	if not ipv4.match(dns_answer):
		host = dot_from_host.sub('', dns_answer)
		dns_answer = resolve(host)
	
	return dns_answer

def get_punycode(url):
	"""Encode domain names.
	
	If the domain name of the 'url' has a domain name in non-Latin format, it will be encoded according to the IDNA.
	
	Usage:
	
	  >>> from unalix import get_punycode
	  >>> get_punycode('http://i❤️.ws/index.html')
	  'http://xn--i-7iq.ws/index.html'
	"""
	
	domain_name = urllib.parse.urlsplit(url).netloc
	
	idna_domain = domain_name.encode('IDNA').decode('UTF-8')
	
	if domain_name != idna_domain:
		url = url.replace(domain_name, idna_domain)
	
	return url

def unshort_url(url):
	"""Try to unshort the URL.
	
	A GET request will be made to the 'url'. All new URLs to which the request tries to redirect will be modified according to the regex rules found in the .json files and will be followed in a new request.
	
	The 'Accept-Language' and 'User-Agent' headers will receive a new value before each request. The values will be replaced by items selected at random from the 'user_agents' and 'languages' lists.
	
	Usage:
	
	  >>> from unalix import unshort_url
	  >>> unshort_url('http://bit.ly/3dfhDq1')
	  'https://g.co/'
	"""
	
	# If the specified 'url' does not have a protocol defined, it will be set to 'http://'
	if not url_schema.match(url):
		url = 'http://' + url
	
	# If the specified URL has a domain name in non-Latin alphabet, the get_punycode() function will return a URL with the domain name encoded according to IDNA
	url = get_punycode(url)
	
	while True:
		with req.get(url, stream=True, allow_redirects=False) as request:
			request.raise_for_status()
		
		if request.is_redirect:
			url = parse_regex_rules(request.next.url)
			req.headers['Accept-Language'] = random.choice(languages)
			req.headers['User-Agent'] = random.choice(user_agents)
		else:
			return request.url
	
	return url
	
def clear_url(url):
	"""Clear and unshort the 'url'
	
	The 'url' will be processed by the parse_regex_rules() and unshort_url() functions.
	
	Usage:
	
	  >>> from unalix import clear_url
	  >>> clear_url('http://g.co/?utm_source=google')
	  'https://g.co/'
	"""
	
	url = parse_regex_rules(url)
	
	url = unshort_url(url)
	
	return url
	
def parse_regex_rules(url):
	"""Process the regex rules found in files 'data.min.json', 'custom-data.min.json' and 'replacements.json'.
	
	The 'url' will be analyzed and the parameters contained in the URL will be removed/replaced according to the regex rules found.
	
	Usage:
	
	  >>> from unalix import parse_regex_rules
	  >>> parse_regex_rules('http://g.co/?utm_source=google')
	  'http://g.co/'
	"""
	
	original_url = url
	
	skip_provider = False
	
	for rules_file in [ 'data.min.json',  'custom-data.min.json' ]:
		with open(rules_dir + rules_file, 'r') as rules_file:
			rules = json.loads(rules_file.read())
		for provider_name in rules['providers'].keys():
			if rules['providers'][provider_name]['completeProvider'] != True:
				for pattern in [ rules['providers'][provider_name]['urlPattern'] ]:
					if re.match(pattern, url):
						for exception in rules['providers'][provider_name]['exceptions']:
							if re.match(exception, url):
								skip_provider = True
								break
						if not skip_provider:
							for redirection_rule in rules['providers'][provider_name]['redirections']:
								url = re.sub(redirection_rule+'.*', '\g<1>', url)
							if url != original_url:
								url = urllib.parse.unquote(url)
								url = requests.utils.requote_uri(url)
							for common_rule in rules['providers'][provider_name]['rules']:
								url = re.sub('(%26|&|%23|#|%3F|%3f|\?)' + common_rule + '(\=[^&]*)', '\g<1>', url)
							for referral_marketing_rule in rules['providers'][provider_name]['referralMarketing']:
								url = re.sub('(%26|&|%23|#|%3F|%3f|\?)' + referral_marketing_rule + '(\=[^&]*)', '\g<1>', url)
							for raw_rule in rules['providers'][provider_name]['rawRules']:
								url = re.sub(raw_rule, '', url)
							original_url = url
	
	for rules_file in [ 'replacements.json' ]:
		with open(rules_dir + rules_file, 'r') as rules_file:
			rules = json.loads(rules_file.read())
		for provider_name in rules['providers'].keys():
			if re.match(rules['providers'][provider_name]['urlPattern'], url):
				replacements = rules['providers'][provider_name]['replacements']
				# 'https://stackoverflow.com/questions/5389507/iterating-over-every-two-elements-in-a-list/48347320#48347320'
				for pattern, replacement in list(zip(*([iter(replacements)] * 2))):
					url = re.sub(pattern, replacement, url)
	
	return url
	