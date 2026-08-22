import hashlib

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Path prefix -> Cache-Control max-age in seconds. Only GET responses
# under these prefixes get an ETag/Cache-Control added -- auth,
# mutations (POST/PUT/PATCH/DELETE), websockets, and GraphQL are left
# untouched. Analytics gets a longer TTL to match the existing Redis
# cache TTL for that data (app/services/analytics_service.py).
_CACHEABLE_PREFIXES: dict[str, int] = {
    "/stations": 60,
    "/trains": 60,
    "/routes": 60,
    "/route-stations": 60,
    "/journeys": 60,
    "/analytics": 300,
}


def _max_age_for_path(path: str) -> int | None:
    for prefix, max_age in _CACHEABLE_PREFIXES.items():
        if path == prefix or path.startswith(prefix + "/"):
            return max_age
    return None


class HttpCachingMiddleware(BaseHTTPMiddleware):
    """
    Adds ETag + Cache-Control to GET responses on read-only endpoints,
    and answers conditional requests (If-None-Match) with 304 instead
    of resending the body. Lets browsers and any CDN in front of this
    API skip re-fetching data that hasn't changed, on top of (not
    instead of) the server-side Redis cache -- this saves the response
    transfer itself, which a server-side cache can't do.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)

        max_age = _max_age_for_path(request.url.path)
        if max_age is None:
            return await call_next(request)

        response = await call_next(request)

        if response.status_code != 200:
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        etag = f'"{hashlib.sha256(body).hexdigest()[:32]}"'
        cache_control = f"public, max-age={max_age}"

        if request.headers.get("if-none-match") == etag:
            return Response(
                status_code=304,
                headers={"ETag": etag, "Cache-Control": cache_control},
            )

        headers = dict(response.headers)
        headers["ETag"] = etag
        headers["Cache-Control"] = cache_control
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )
