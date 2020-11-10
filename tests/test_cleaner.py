from unalix import clear_url

def test_clear_url():

    unmodified_url = "https://deezer.com/track/891177062?utm_source=deezer"

    assert clear_url(unmodified_url) == "https://deezer.com/track/891177062"
    assert clear_url(unmodified_url, ignore_rules=True) == unmodified_url

    unmodified_url = "https://www.google.com/url?q=https://pypi.org/project/Unalix"

    assert clear_url(unmodified_url) == "https://pypi.org/project/Unalix"
    assert clear_url(unmodified_url, ignore_redirections=True) == unmodified_url

    unmodified_url = "https://www.amazon.com/gp/B08CH7RHDP/ref=as_li_ss_tl"

    assert clear_url(unmodified_url) == "https://www.amazon.com/gp/B08CH7RHDP"
    assert clear_url(unmodified_url, ignore_raw=True) == unmodified_url

    unmodified_url = "http://0.0.0.0/?utm_source=local"

    assert clear_url(unmodified_url) == "http://0.0.0.0/"
    assert clear_url(unmodified_url, skip_local=True) == unmodified_url

    unmodified_url = "https://natura.com.br/p/2458?consultoria=promotop"

    assert clear_url(unmodified_url) == "https://natura.com.br/p/2458"
    assert clear_url(unmodified_url, allow_referral=True) == unmodified_url

    unmodified_url = "https://myaccount.google.com/?utm_source=google"

    assert clear_url(unmodified_url) == unmodified_url
    assert clear_url(unmodified_url, ignore_exceptions=True) == "https://myaccount.google.com/"

    unmodified_url = "http://clickserve.dartsearch.net/link/click?ds_dest_url=https://www.target.com/s/minecraft"

    assert clear_url(unmodified_url) == "https://www.target.com/s/minecraft"
    assert clear_url(unmodified_url, skip_blocked=True) == unmodified_url

    unmodified_url = "http://example.com/?p1&p2=&p3=p=&&p4=v"

    assert clear_url(unmodified_url) == "http://example.com/?p4=v"

