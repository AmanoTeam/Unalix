from unalix import clearUrl

def test_clearUrl():

    unmodified_url = "https://deezer.com/track/891177062?utm_source=deezer"

    assert clearUrl(unmodified_url) == "https://deezer.com/track/891177062"
    assert clearUrl(unmodified_url, ignoreRules=True) == unmodified_url
    
    unmodified_url = "https://www.google.com/url?q=https://pypi.org/project/Unalix"

    assert clearUrl(unmodified_url) == "https://pypi.org/project/Unalix"
    assert clearUrl(unmodified_url, ignoreRedirections=True) == unmodified_url
    
    unmodified_url = "https://www.google.com/amp/s/de.statista.com/infografik/amp/22496/anzahl-der-gesamten-positiven-corona-tests-und-positivenrate/"
    assert clearUrl(unmodified_url) == "http://de.statista.com/infografik/amp/22496/anzahl-der-gesamten-positiven-corona-tests-und-positivenrate/"

    unmodified_url = "http://www.shareasale.com/r.cfm?u=1384175&b=866986&m=65886&afftrack=&urllink=www.rightstufanime.com%2Fsearch%3Fkeywords%3DSo%20I%27m%20a%20Spider%20So%20What%3F"
    assert clearUrl(unmodified_url) == "http://www.rightstufanime.com/search?keywords=So%20I'm%20a%20Spider%20So%20What%3F"

    unmodified_url = "https://www.amazon.com/gp/B08CH7RHDP/ref=as_li_ss_tl"

    assert clearUrl(unmodified_url) == "https://www.amazon.com/gp/B08CH7RHDP"
    assert clearUrl(unmodified_url, ignoreRawRules=True) == unmodified_url
    
    unmodified_url = "http://0.0.0.0/?utm_source=local"

    assert clearUrl(unmodified_url) == "http://0.0.0.0/"
    assert clearUrl(unmodified_url, skipLocal=True) == unmodified_url
    
    unmodified_url = "https://natura.com.br/p/2458?consultoria=promotop"

    assert clearUrl(unmodified_url) == "https://natura.com.br/p/2458"
    assert clearUrl(unmodified_url, ignoreReferralMarketing=True) == unmodified_url

    unmodified_url = "https://myaccount.google.com/?utm_source=google"

    assert clearUrl(unmodified_url) == unmodified_url
    assert clearUrl(unmodified_url, ignoreExceptions=True) == "https://myaccount.google.com/"

    unmodified_url = "http://clickserve.dartsearch.net/link/click?ds_dest_url=http://g.co/"

    assert clearUrl(unmodified_url) == "http://g.co/"
    assert clearUrl(unmodified_url, skipBlocked=True) == unmodified_url

    unmodified_url = "http://example.com/?p1=&p2="

    assert clearUrl(unmodified_url) == unmodified_url
    assert clearUrl(unmodified_url, stripEmpty=True) == "http://example.com/"

    unmodified_url = "http://example.com/?p1=value&p1=othervalue"

    assert clearUrl(unmodified_url) == unmodified_url
    assert clearUrl(unmodified_url, stripDuplicates=True) == "http://example.com/?p1=value"

    unmodified_url = "http://example.com/?&&&&"

    assert clearUrl(unmodified_url) == "http://example.com/"
    
    # https://github.com/AmanoTeam/Unalix-nim/issues/5
    unmodified_url = "https://docs.julialang.org/en/v1/stdlib/REPL/#Key-bindings"
    assert clearUrl(unmodified_url) == unmodified_url
    