import re

import httpx
from fastapi import FastAPI, Request
from starlette.background import BackgroundTask
from starlette.responses import Response, StreamingResponse


BACKEND = "http://127.0.0.1:7000"
proxy_app = FastAPI()

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

DROP_RESPONSE_HEADERS = {
    "content-security-policy",
    "x-frame-options",
    "content-length",
    "content-encoding",
}


def _ingress_base(request: Request) -> str:
    base = request.headers.get("x-ingress-path", "").strip()
    if base.endswith("/"):
        base = base[:-1]
    return base


def _backend_path(request: Request, base: str) -> str:
    path = request.url.path or "/"
    if base and path.startswith(base):
        path = path[len(base):] or "/"
    return path


def _backend_url(request: Request, base: str) -> str:
    query = request.url.query
    path = _backend_path(request, base)
    return f"{BACKEND}{path}" + (f"?{query}" if query else "")


def _request_headers(request: Request) -> dict:
    headers = {}
    for key, value in request.headers.items():
        lk = key.lower()
        if lk in HOP_BY_HOP_HEADERS or lk == "host":
            continue
        headers[key] = value
    headers["host"] = "127.0.0.1:7000"
    headers["x-forwarded-host"] = request.headers.get("host", "")
    headers["x-forwarded-proto"] = request.url.scheme
    headers["x-forwarded-for"] = request.client.host if request.client else ""
    return headers


def _response_headers(response: httpx.Response, base: str) -> dict:
    headers = {}
    for key, value in response.headers.items():
        lk = key.lower()
        if lk in HOP_BY_HOP_HEADERS or lk in DROP_RESPONSE_HEADERS:
            continue
        if lk == "location" and base and value.startswith("/"):
            value = f"{base}{value}"
        headers[key] = value
    return headers


def _rewrite_text(text: str, content_type: str, base: str) -> str:
    if not base:
        return text

    if "text/html" in content_type:
        bootstrap = f"""
<script>
(function() {{
  const base = {base!r};
  window.__ODYSSEUS_BASE_PATH__ = base;
  const rewrite = (url) => {{
    if (typeof url !== 'string') return url;
    const targets = /^\\/(api|static|login|notes|calendar|cookbook|email|memory|gallery|tasks|library|backgrounds)(\\/|$)/;
    try {{
      const parsed = new URL(url, window.location.origin);
      if (parsed.origin === window.location.origin && targets.test(parsed.pathname)) {{
        return base + parsed.pathname + parsed.search + parsed.hash;
      }}
    }} catch (_) {{}}
    if (url.startsWith(base + '/')) return url;
    if (targets.test(url)) return base + url;
    return url;
  }};
  const oldFetch = window.fetch;
  window.fetch = function(input, init) {{
    if (typeof input === 'string') input = rewrite(input);
    else if (input && input.url) input = new Request(rewrite(input.url), input);
    return oldFetch.call(this, input, init);
  }};
  const oldOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) {{
    arguments[1] = rewrite(url);
    return oldOpen.apply(this, arguments);
  }};
  const OldEventSource = window.EventSource;
  if (OldEventSource) window.EventSource = function(url, cfg) {{ return new OldEventSource(rewrite(url), cfg); }};
  const OldWebSocket = window.WebSocket;
  if (OldWebSocket) window.WebSocket = function(url, protocols) {{ return new OldWebSocket(rewrite(url), protocols); }};
  if (navigator.serviceWorker) {{
    const oldRegister = navigator.serviceWorker.register.bind(navigator.serviceWorker);
    navigator.serviceWorker.register = function(url, opts) {{ return oldRegister(rewrite(url), opts); }};
  }}
}})();
</script>
"""
        text = text.replace("</head>", bootstrap + "</head>")

    if "javascript" in content_type or "text/html" in content_type:
        text = text.replace(
            "const API_BASE = window.location.origin;",
            "const API_BASE = window.location.origin + (window.__ODYSSEUS_BASE_PATH__ || '');",
        )

    replacements = [
        ('href="/', f'href="{base}/'),
        ('src="/', f'src="{base}/'),
        ('action="/', f'action="{base}/'),
        ("href='/", f"href='{base}/"),
        ("src='/", f"src='{base}/"),
        ("action='/", f"action='{base}/"),
        ('url("/', f'url("{base}/'),
        ("url('/", f"url('{base}/"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    if any(kind in content_type for kind in ("javascript", "text/css", "text/html")):
        text = re.sub(
            r"(?P<quote>['\"`])/(?P<path>api|static|login|notes|calendar|cookbook|email|memory|gallery|tasks|library|backgrounds)(?P<tail>[/\?'\"]|`)",
            lambda m: f"{m.group('quote')}{base}/{m.group('path')}{m.group('tail')}",
            text,
        )
    return text


def _is_rewriteable(content_type: str) -> bool:
    return any(
        marker in content_type
        for marker in (
            "text/html",
            "text/css",
            "javascript",
            "application/manifest+json",
        )
    )


@proxy_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy(request: Request):
    base = _ingress_base(request)
    body = await request.body()
    client = httpx.AsyncClient(timeout=None, follow_redirects=False)
    backend_response = await client.send(
        client.build_request(
            request.method,
            _backend_url(request, base),
            headers=_request_headers(request),
            content=body,
        ),
        stream=True,
    )

    content_type = backend_response.headers.get("content-type", "")
    headers = _response_headers(backend_response, base)

    if _is_rewriteable(content_type):
        payload = await backend_response.aread()
        await backend_response.aclose()
        await client.aclose()
        text = payload.decode(backend_response.encoding or "utf-8", errors="replace")
        rewritten = _rewrite_text(text, content_type, base).encode("utf-8")
        return Response(
            rewritten,
            status_code=backend_response.status_code,
            headers=headers,
            media_type=content_type.split(";", 1)[0],
        )

    async def stream_response():
        try:
            async for chunk in backend_response.aiter_bytes():
                yield chunk
        finally:
            await backend_response.aclose()
            await client.aclose()

    return StreamingResponse(
        stream_response(),
        status_code=backend_response.status_code,
        headers=headers,
        media_type=content_type or None,
        background=BackgroundTask(lambda: None),
    )
