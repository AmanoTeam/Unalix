import string
import urllib.parse

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L566
# The unreserved URI characters (RFC 3986)
UNRESERVED_SET = frozenset(
	string.ascii_uppercase + string.ascii_lowercase + string.digits + "-._~"
)

# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L570
def unquote_unreserved(uri):
	"""Un-escape any percent-escape sequences in a URI that are unreserved
	characters. This leaves all reserved, illegal and non-ASCII bytes encoded.
	"""
	parts = uri.split("%")
	for i in range(1, len(parts)):
		h = parts[i][0:2]
		if len(h) == 2 and h.isalnum():
			c = chr(int(h, 16))
			if c in UNRESERVED_SET:
				parts[i] = c + parts[i][2:]
			else:
				parts[i] = "%" + parts[i]
		else:
			parts[i] = "%" + parts[i]
	return "".join(parts)


# https://github.com/psf/requests/blob/v2.24.0/requests/utils.py#L594
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
		return urllib.parse.quote(unquote_unreserved(uri), safe=safe_with_percent)
	except ValueError:
		# We couldn't unquote the given URI, so let"s try quoting it, but
		# there may be unquoted "%"s in the URI. We need to make sure they're
		# properly quoted so they do not cause issues elsewhere.
		return urllib.parse.quote(uri, safe=safe_without_percent)

