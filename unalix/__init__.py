from json import loads
from re import match, sub
from requests import head
from requests.utils import unquote, requote_uri
from urllib.parse import urlsplit
from os.path import dirname, join

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

work_dir = dirname(__file__)

def clear_url(url):
    
    if match('^(?![a-z]+://)', url):
        url = 'http://' + url
    
    domain_name = urlsplit(url).netloc
    
    idna_domain = domain_name.encode('idna').decode()
    
    if domain_name != idna_domain:
        url = url.replace(domain_name, idna_domain)
    
    try:
        with head(url, headers=headers, allow_redirects=True, timeout=5) as r:
            url = r.url
    except:
        pass
    
    original_url = url
    
    for rules_file in [ 'rules/data.min.json',  'rules/custom-data.min.json' ]:
        with open(join(work_dir,  rules_file)) as rules_file:
            rules = loads(rules_file.read())
        for provider_name in rules['providers'].keys():
            if rules['providers'][provider_name]['completeProvider'] != True:
                for pattern in [ rules['providers'][provider_name]['urlPattern'] ]:
                    if match(pattern, url):
                        for exception in rules['providers'][provider_name]['exceptions']:
                            if match(exception, url):
                                skip_provider = True
                                break
                        try:
                            skip_provider
                        except:
                            for redirection_rule in rules['providers'][provider_name]['redirections']:
                                url = sub(redirection_rule+'.*', '\g<1>', url)
                            if url != original_url:
                                url = unquote(url)
                            for common_rule in rules['providers'][provider_name]['rules']:
                                url = sub('(%26|&|%23|#|%3F|%3f|\?)+'+common_rule+'(\=[^&]*)', '\g<1>', url)
                            for referral_marketing_rule in rules['providers'][provider_name]['referralMarketing']:
                                url = sub('(%26|&|%23|#|%3F|%3f|\?)+'+referral_marketing_rule+'(\=[^&]*)', '\g<1>', url)
                            for raw_rule in rules['providers'][provider_name]['rawRules']:
                                url = sub(raw_rule, '', url)
                            original_url = url
    
    for rules_file in [ 'rules/special_rules.json' ]:
        with open(join(work_dir,  rules_file)) as rules_file:
            rules = loads(rules_file.read())
        for provider_name in rules['providers'].keys():
            if match(rules['providers'][provider_name]['urlPattern'], url):
                for special_rule in rules['providers'][provider_name]['rules']:
                    pattern = sub('^(.*)\s<\->\s.*$', '\g<1>', special_rule)
                    replace = sub('^.*\s<\->\s(.*)$', '\g<1>', special_rule)
                    url = sub(pattern, replace, url)
    
    url = requote_uri(url)
    
    return url

