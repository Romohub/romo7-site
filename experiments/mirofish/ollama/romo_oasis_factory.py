"""Native local CAMEL backend so OASIS receives structured tool calls."""
import os
from urllib.parse import urlsplit


def create_local_oasis_model():
    base = os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
    p = urlsplit(base)
    if (p.scheme != 'http' or p.hostname not in ('127.0.0.1', 'localhost', '::1')
            or p.username or p.password or p.path or p.query or p.fragment):
        raise ValueError('OASIS Ollama experiment requires a plain loopback URL')
    model = os.environ.get('OLLAMA_MODEL', 'qwen3.5:4b')
    if model != 'qwen3.5:4b':
        raise ValueError('Unverified model is not permitted')
    from camel.models.ollama_model import OllamaModel
    return OllamaModel(model_type=model, url=base+'/v1', api_key='local-only',
                       model_config_dict={'temperature': 0, 'max_tokens': 1024},
                       timeout=90, max_retries=0)
