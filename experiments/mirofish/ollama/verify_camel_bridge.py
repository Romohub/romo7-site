"""Real CAMEL/OpenAI SDK with an HTTP fixture; never calls a live model."""
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from romo_oasis_factory import create_local_oasis_model

requests = []
tool = {'type':'function', 'function':{'name':'create_post', 'description':'Local fixture only',
        'parameters':{'type':'object','properties':{'text':{'type':'string'}},'required':['text']}}}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        requests.append((self.path,json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
        body = {'id':'fixture-1','object':'chat.completion','created':1,'model':'qwen3.5:4b',
                'choices':[{'index':0,'finish_reason':'tool_calls','message':{'role':'assistant',
                'content':None,'tool_calls':[{'id':'call-1','type':'function',
                'function':{'name':'create_post','arguments':'{"text":"fixture"}'}}]}}]}
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
    def log_message(self,*args): pass

server = HTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
os.environ['OLLAMA_BASE_URL']='http://127.0.0.1:'+str(server.server_port)
os.environ['OLLAMA_MODEL']='qwen3.5:4b'
try:
    model = create_local_oasis_model()
    completion = model._request_chat_completion([{'role':'user','content':'fixture only'}],tools=[tool])
    assert requests[0][0] == '/v1/chat/completions', requests
    assert requests[0][1]['tools'] == [tool], requests
    call = completion.choices[0].message.tool_calls[0]
    assert call.function.name == 'create_post'
    assert json.loads(call.function.arguments) == {'text':'fixture'}
    print('REAL_CAMEL_TOOL_BRIDGE_PASS; HTTP fixture; live_model_calls=0; simulations=0')
finally:
    server.shutdown()
    server.server_close()
