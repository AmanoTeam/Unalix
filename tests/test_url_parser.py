from unalix._core import parse_url

def test_parse_url():

    unmodified_url = "xn--i-7iq.ws"

    if parse_url(unmodified_url) != "http://xn--i-7iq.ws":
        raise AssertionError

    unmodified_url = "i❤️.ws"

    if parse_url(unmodified_url) != "http://xn--i-7iq.ws":
        raise AssertionError

    unmodified_url = "http://user:pass@xn--i-7iq.ws/"

    if parse_url(unmodified_url) != "http://xn--i-7iq.ws/":
        raise AssertionError
