from .settings import (
	user_agents, languages, doh, req, rules_dir
)
import json
import random
import re
import requests
import urllib
import urllib3

ipv4 = re.compile(
	r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
)

 # https://stackoverflow.com/questions/22609385/python-requests-library-define-specific-dns/22614367#22614367
def patched_create_connection(address, *args, **kwargs):
	host, port = address
	hostname = resolve(host)
	
	return _orig_create_connection(
		(hostname, port), *args, **kwargs
	)

_orig_create_connection = urllib3.util.connection.create_connection
urllib3.util.connection.create_connection = patched_create_connection

def resolve(host):
	"""Resolve domain names using DNS-over-HTTPS.
	
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
	
	doh_url = 'https://fi.doh.dns.snopyta.org/dns-query'
	
	request = doh.get(doh_url, params=params)
	request.close()
	
	json_response = request.json()
	
	dns_answer = json_response['Answer'][0]['data']
	
	if not ipv4.match(dns_answer):
		host = dns_answer.strip('.')
		dns_answer = resolve(host)
	
	return dns_answer

def get_punycode(url):
	"""Encode domain names.
	
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
	
	Usage:
	
	  >>> from unalix import unshort_url
	  >>> unshort_url('http://bit.ly/3dfhDq1')
	  'https://g.co/'
	"""
	
	# If the specified :url: does not have a protocol defined, it will be set to 'http://'
	if not url.startswith('https://') and not url.startswith('http://'):
		url = 'http://' + url
	
	# If the specified URL has a domain name in non-Latin alphabet, the get_punycode() function will return a URL with the domain name encoded according to IDNA
	url = get_punycode(url)
	
	while True:
		request = req.get(url, stream=True, allow_redirects=False)
		request.close()
		
		if request.is_redirect:
			# Clear the url before following the redirect
			url = parse_regex_rules(request.next.url)
			req.headers.update(
				{
					'Accept-Language': random.choice(languages),
					'User-Agent': random.choice(user_agents)
				}
			)
		else:
			return request.url
	
	return url
	
def clear_url(url):
	"""Clear and unshort the :url:
	
	Usage:
	
	  >>> from unalix import clear_url
	  >>> clear_url('http://g.co/?utm_source=google')
	  'https://g.co/'
	"""
	
	url = parse_regex_rules(url)
	
	url = unshort_url(url)
	
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
	