"""Tests the actual pinned LLMClient through a local HTTP fixture; no live model."""
import importlib
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch
from install_adapter import install

source_root = Path(sys.argv.pop(1)).resolve()
temp_root = tempfile.TemporaryDirectory()
root = Path(temp_root.name)
for rel in ('app/config.py', 'app/cli.py', 'app/utils/llm_client.py'):
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_root / rel, target)
install(root)
install(root)  # repeated preparation must not duplicate the dispatch branch
if (source_root / 'app/utils/oasis_llm.py').exists():
    shutil.copyfile(source_root / 'app/utils/oasis_llm.py', root / 'app/utils/oasis_llm.py')
    install(root)
for name, path in (('app', root/'app'), ('app.utils', root/'app/utils')):
    mod = types.ModuleType(name)
    mod.__path__ = [str(path)]
    sys.modules[name] = mod
dotenv = types.ModuleType('dotenv')
dotenv.load_dotenv = lambda **kwargs: None
sys.modules['dotenv'] = dotenv
logger = types.ModuleType('app.utils.logger')
logger.get_logger = logging.getLogger
sys.modules['app.utils.logger'] = logger
os.environ['LLM_PROVIDER'] = 'ollama'
from app.config import Config
from app.utils.llm_client import LLMClient


class Handler(BaseHTTPRequestHandler):
    result = {}
    requests = []
    def do_POST(self):
        self.requests.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(self.result).encode())
    def log_message(self, *args):
        pass


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
    def setUp(self):
        self.env = patch.dict(os.environ, {'OLLAMA_BASE_URL': 'http://127.0.0.1:'+str(self.server.server_port), 'OLLAMA_MODEL': 'qwen3.5:4b'})
        self.env.start()
        self.addCleanup(self.env.stop)
        Handler.requests = []
        Handler.result = {'model': 'qwen3.5:4b', 'done': True, 'message': {'content': '{"ok":true}'}}
        self.client = LLMClient()
    def test_config_accepts_provider(self):
        self.assertEqual(Config.validate(), [])
    def test_actual_chat_preserves_messages_and_caps_tokens(self):
        msgs = [{'role': 'system', 'content':'test'}, {'role':'user', 'content':'hello'}]
        self.assertEqual(self.client.chat(msgs, max_tokens=10000), '{"ok":true}')
        path, body = Handler.requests[0]
        self.assertEqual(path, '/api/chat')
        self.assertEqual(body['messages'], msgs)
        self.assertEqual(body['options']['num_predict'], 2048)
        self.assertFalse(body['think'])
    def test_actual_chat_json(self):
        self.assertEqual(self.client.chat_json([{'role':'user','content':'test'}]), {'ok': True})
        self.assertEqual(Handler.requests[0][1]['format'], 'json')
    def test_rejects_external_endpoint_before_request(self):
        os.environ['OLLAMA_BASE_URL'] = 'https://ollama.com'
        with self.assertRaises(ValueError): self.client.chat([])
        self.assertEqual(Handler.requests, [])
    def test_rejects_cloud_model_before_request(self):
        os.environ['OLLAMA_MODEL'] = 'other:cloud'
        with self.assertRaises(ValueError): self.client.chat([])
        self.assertEqual(Handler.requests, [])
    def test_rejects_truncated_response(self):
        Handler.result['done_reason'] = 'length'
        with self.assertRaises(ValueError): self.client.chat([])
        self.assertEqual(len(Handler.requests), 1)
    def test_rejects_empty_response(self):
        Handler.result['message']['content'] = ''
        with self.assertRaises(ValueError): self.client.chat([])
    def test_rejects_wrong_response_model(self):
        Handler.result['model'] = 'unexpected'
        with self.assertRaises(ValueError): self.client.chat([])
    def test_native_oasis_backend_configuration(self):
        if not (root / 'app/utils/oasis_llm.py').exists(): self.fail('OASIS source missing')
        import ast
        from app.utils.romo_oasis_factory import create_local_oasis_model
        backend = types.ModuleType('camel.models.ollama_model')
        backend.OllamaModel = lambda **kwargs: kwargs
        with patch.dict(sys.modules, {'camel.models.ollama_model': backend}):
            tree = ast.parse((root / 'app/utils/oasis_llm.py').read_text())
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'create_oasis_model')
            ns = dict(os=os, Config=Config, logger=logging.getLogger('test'), Dict=dict, Any=object, __package__='app.utils')
            exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])), '<factory>', 'exec'), ns)
            result = ns['create_oasis_model']({})
            self.assertEqual(result['model_type'], 'qwen3.5:4b')
            self.assertTrue(result['url'].endswith('/v1'))
            self.assertEqual(result['max_retries'], 0)
    def test_native_backend_rejects_remote_url(self):
        from app.utils.romo_oasis_factory import create_local_oasis_model
        os.environ['OLLAMA_BASE_URL'] = 'https://remote.example'
        with self.assertRaises(ValueError): create_local_oasis_model()


if __name__ == '__main__':
    unittest.main(verbosity=2)
