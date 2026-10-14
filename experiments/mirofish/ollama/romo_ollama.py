"""Loopback-only Ollama provider for the pinned MiroFish experiment."""
import json
import os
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def chat(messages, temperature, max_tokens, response_format=None):
    base = os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
    parsed = urlsplit(base)
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1')
            or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise ValueError('Ollama experiment requires a plain HTTP loopback URL')
    model = os.environ.get('OLLAMA_MODEL', 'qwen3.5:4b')
    if model != 'qwen3.5:4b':
        raise ValueError('Only the verified local qwen3.5:4b model is authorized for this experiment')
    payload = dict(model=model, messages=messages, stream=False, think=False,
                   options=dict(temperature=temperature, num_predict=min(max(1, int(max_tokens)), 2048),
                                num_ctx=8192))
    if response_format and response_format.get('type') == 'json_object':
        payload['format'] = 'json'
    req = Request(base + '/api/chat', data=json.dumps(payload).encode('utf-8'),
                  headers={'Content-Type': 'application/json'}, method='POST')
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=90) as response:
            raw = response.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError('Ollama response exceeded experiment limit')
        result = json.loads(raw)
        if result.get('model') != model or result.get('done') is not True:
            raise ValueError('Incomplete response or unexpected model')
        if result.get('done_reason') == 'length':
            raise ValueError('Ollama response truncated at token limit')
        content = result.get('message', {}).get('content')
        if not isinstance(content, str) or not content.strip():
            raise ValueError('Ollama returned no content')
        return content
    except (OSError, TimeoutError) as exc:
        raise RuntimeError('Local Ollama request failed') from exc
