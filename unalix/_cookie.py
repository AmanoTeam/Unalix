from http.cookiejar import DefaultCookiePolicy

default_policy = DefaultCookiePolicy()

def set_ok(cookie, request):
    return True

default_policy.set_ok = set_ok