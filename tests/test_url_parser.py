from unalix._core import parse_url

def test_parse_url():

    unmodified_url = "xn--i-7iq.ws"

    assert parse_url(unmodified_url) == "http://xn--i-7iq.ws"

    unmodified_url = "i❤️.ws"

    assert parse_url(unmodified_url) == "http://xn--i-7iq.ws"

    unmodified_url = "http://user:pass@xn--i-7iq.ws/"

    assert parse_url(unmodified_url) == "http://xn--i-7iq.ws/"


