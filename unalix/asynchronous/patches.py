import functools
import random
import typing

from .http_clients import client
from ..settings import user_agents, languages
from .utils import parse_regex_rules

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
from httpx._utils import get_logger

logger = get_logger(__name__)

async def patched_send_handling_redirects(
	request: Request,
	auth: Auth,
	timeout: Timeout,
	allow_redirects: bool = True,
	history: typing.List[Response] = None,
) -> Response:
	if history is None:
		history = []

	while True:
		if len(history) > client.max_redirects:
			raise TooManyRedirects(
				"Exceeded maximum allowed redirects.", request=request
			)

		response = await client._send_handling_auth(
			request, auth=auth, timeout=timeout, history=history
		)
		response.history = list(history)

		if not response.is_redirect:
			return response

		if allow_redirects:
			await response.aread()
		request = client._build_redirect_request(request, response)
		history = history + [response]

		url = await parse_regex_rules(str(request.url))
		request.url = URL(url)
		
		request.headers.update({
			'Accept-Language': random.choice(languages),
			'Referer': url,
			'User-Agent': random.choice(user_agents),
		})
		
		if request.url.scheme == 'http':
			request.headers.update({
				'Upgrade-Insecure-Requests': '1'
			})
	
		if not allow_redirects:
			response.call_next = functools.partial(
				client._send_handling_redirects,
				request=request,
				auth=auth,
				timeout=timeout,
				allow_redirects=False,
				history=history,
			)
			return response


client._send_handling_redirects = patched_send_handling_redirects

async def patched_send(
	request: Request,
	*,
	stream: bool = False,
	auth: AuthTypes = None,
	allow_redirects: bool = True,
	timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
) -> Response:
	timeout = client.timeout if isinstance(timeout, UnsetType) else Timeout(timeout)
	
	auth = client._build_auth(request, auth)
	
	request.headers.update({
		'Accept-Language': random.choice(languages),
		'Referer': str(request.url),
		'User-Agent': random.choice(user_agents)
	})
	
	if request.url.scheme == 'http':
		request.headers.update({
			'Upgrade-Insecure-Requests': '1'
		})
	
	response = await client._send_handling_redirects(
		request, auth=auth, timeout=timeout, allow_redirects=allow_redirects,
	)
	
	if not stream:
		try:
			await response.aread()
		finally:
			await response.aclose()
	
	await response.aclose()
	return response

client.send = patched_send

async def patched_send_single_request(
	request: Request, timeout: Timeout,
) -> Response:
	"""
	Sends a single request, without handling any redirections.
	"""
	transport = client._transport_for_url(request.url)
	
	with map_exceptions(HTTPCORE_EXC_MAP, request=request):
		(
			http_version,
			status_code,
			reason_phrase,
			headers,
			stream,
		) = await transport.request(
			request.method.encode(),
			request.url.raw,
			headers=request.headers.raw,
			stream=request.stream,
			timeout=timeout.as_dict(),
		)
	response = Response(
		status_code,
		http_version=http_version.decode("ascii"),
		headers=headers,
		stream=stream,  # type: ignore
		request=request,
	)
	
	status = f"{response.status_code} {response.reason_phrase}"
	response_line = f"{response.http_version} {status}"
	logger.debug(f'HTTP Request: {request.method} {request.url} "{response_line}"')
	
	response.raise_for_status()
	
	return response

client._send_single_request = patched_send_single_request
