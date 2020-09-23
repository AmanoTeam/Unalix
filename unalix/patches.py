import functools
import random
import typing
import datetime

from httpx._auth import Auth
from httpx._config import Timeout, UNSET, UnsetType
from httpx._exceptions import (
	TooManyRedirects,
	map_exceptions,
	HTTPCORE_EXC_MAP
)
from httpx._models import URL, Request, Response
from httpx._types import (
	AuthTypes,
	CertTypes,
	CookieTypes,
	HeaderTypes,
	ProxiesTypes,
	QueryParamTypes,
	RequestData,
	RequestFiles,
	TimeoutTypes,
	URLTypes,
	VerifyTypes,
)
from httpx._utils import get_logger, Timer

from unalix.http_clients import client
from unalix.files import user_agents
from unalix.utils import parse_rules

logger = get_logger(__name__)

def send(
	request: Request,
	*,
	stream: bool = False,
	auth: typing.Union[AuthTypes, UnsetType] = UNSET,
	allow_redirects: bool = True,
	timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
) -> Response:
	"""
	Send a request.

	The request is sent as-is, unmodified.

	Typically you'll want to build one with `Client.build_request()`
	so that any client-level configuration is merged into the request,
	but passing an explicit `httpx.Request()` is supported as well.

	See also: [Request instances][0]

	[0]: /advanced/#request-instances
	"""
	client._is_closed = False

	timeout = client.timeout if isinstance(timeout, UnsetType) else Timeout(timeout)

	auth = client._build_request_auth(request, auth)

	url = parse_rules(str(request.url))
	request.url = URL(url)

	request.headers.update({
		'User-Agent': random.choice(user_agents)
	})

	if request.url.scheme == 'http':
		request.headers.update({
			'Upgrade-Insecure-Requests': '1'
		})

	response = client._send_handling_auth(
		request,
		auth=auth,
		timeout=timeout,
		allow_redirects=allow_redirects,
		history=[],
	)
	
	response.raise_for_status()

	if not stream:
		try:
			response.read()
		finally:
			response.close()

	try:
		for hook in client._event_hooks["response"]:
			hook(response)
	except Exception:
		response.close()
		raise

	return response

def _send_handling_redirects(
	request: Request,
	timeout: Timeout,
	allow_redirects: bool,
	history: typing.List[Response],
) -> Response:
	while True:
		if len(history) > client.max_redirects:
			raise TooManyRedirects(
				"Exceeded maximum allowed redirects.", request=request
			)

		url = parse_rules(str(request.url))
		request.url = URL(url)

		request.headers.update({
			'User-Agent': random.choice(user_agents),
		})

		if request.url.scheme == 'http':
			request.headers.update({
				'Upgrade-Insecure-Requests': '1'
			})
		else:
			try:
				del request.headers['Upgrade-Insecure-Requests']
			except KeyError:
				pass

		response = client._send_single_request(request, timeout)
		response.history = list(history)

		response.raise_for_status()

		if not response.is_redirect:
			return response

		if allow_redirects:
			response.read()
		request = client._build_redirect_request(request, response)
		history = history + [response]

		if not allow_redirects:
			response.call_next = functools.partial(
				client._send_handling_redirects,
				request=request,
				timeout=timeout,
				allow_redirects=False,
				history=history,
			)
			return response

def _send_single_request(request: Request, timeout: Timeout) -> Response:
	"""
	Sends a single request, without handling any redirections.
	"""
	transport = client._transport_for_url(request.url)
	timer = Timer()
	timer.sync_start()

	with map_exceptions(HTTPCORE_EXC_MAP, request=request):
		(status_code, headers, stream, ext) = transport.request(
			request.method.encode(),
			request.url.raw,
			headers=request.headers.raw,
			stream=request.stream,  # type: ignore
			ext={"timeout": timeout.as_dict()},
		)

	def on_close(response: Response) -> None:
		response.elapsed = datetime.timedelta(timer.sync_elapsed())
		if hasattr(stream, "close"):
			stream.close()

	response = Response(
		status_code,
		headers=headers,
		stream=stream,  # type: ignore
		ext=ext,
		request=request,
		on_close=on_close,
	)

	status = f"{response.status_code} {response.reason_phrase}"
	response_line = f"{response.http_version} {status}"
	logger.debug(f'HTTP Request: {request.method} {request.url} "{response_line}"')

	response.raise_for_status()

	return response

client._send_single_request = _send_single_request
client.send = send
client._send_handling_redirects = _send_handling_redirects