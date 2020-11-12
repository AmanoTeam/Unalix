from unalix import clear_url

def test_clear_url():

    unmodified_url = "https://deezer.com/track/891177062?utm_source=deezer"

    if clear_url(unmodified_url) != "https://deezer.com/track/891177062":
        raise AssertionError
    if clear_url(unmodified_url, ignore_rules=True) != unmodified_url:
        raise AssertionError

    unmodified_url = "https://www.google.com/url?q=https://pypi.org/project/Unalix"

    if clear_url(unmodified_url) != "https://pypi.org/project/Unalix":
        raise AssertionError
    if clear_url(unmodified_url, ignore_redirections=True) != unmodified_url:
        raise AssertionError

    unmodified_url = "https://www.amazon.com/gp/B08CH7RHDP/ref=as_li_ss_tl"

    if clear_url(unmodified_url) != "https://www.amazon.com/gp/B08CH7RHDP":
        raise AssertionError
    if clear_url(unmodified_url, ignore_raw=True) != unmodified_url:
        raise AssertionError

    unmodified_url = "http://0.0.0.0/?utm_source=local"

    if clear_url(unmodified_url) != "http://0.0.0.0/":
        raise AssertionError
    if clear_url(unmodified_url, skip_local=True) != unmodified_url:
        raise AssertionError

    unmodified_url = "https://natura.com.br/p/2458?consultoria=promotop"

    if clear_url(unmodified_url) != "https://natura.com.br/p/2458":
        raise AssertionError
    if clear_url(unmodified_url, allow_referral=True) != unmodified_url:
        raise AssertionError

    unmodified_url = "https://myaccount.google.com/?utm_source=google"

    if clear_url(unmodified_url) != unmodified_url:
        raise AssertionError
    if clear_url(unmodified_url, ignore_exceptions=True) != "https://myaccount.google.com/":
        raise AssertionError

    unmodified_url = "http://clickserve.dartsearch.net/link/click?ds_dest_url=http://g.co/"

    if clear_url(unmodified_url) != "http://g.co/":
        raise AssertionError
    if clear_url(unmodified_url, skip_blocked=True) != unmodified_url:
        raise AssertionError

    unmodified_url = "http://example.com/?p1&p2=&p3=p=&&p4=v"

    if clear_url(unmodified_url) != "http://example.com/?p4=v":
        raise AssertionError

