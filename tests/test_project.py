import json
import pytest
from fastapi.testclient import TestClient
from app.benchmark import CASES,parse,evaluate,OllamaError
from app.main import create_app

def test_parse_valid():assert parse('{"category":"billing","priority":"normal"}')=={'category':'billing','priority':'normal'}
@pytest.mark.parametrize('raw',['garbage','{}','[]','{"category":"wrong","priority":"high"}','{"category":"billing","priority":"normal","extra":1}'])
def test_invalid_outputs(raw):assert parse(raw) is None
def test_exact_scoring_and_throughput():
    by_text={c['text']:c for c in CASES}
    def fake(model,text):
        c=by_text[text];return {'raw':json.dumps({'category':c['category'],'priority':c['priority']}),'wall':2.0,'eval_count':20,'eval_duration':1_000_000_000}
    r=evaluate(['a','b'],fake)
    assert len(r)==2 and all(x['exact_count']==6 and x['valid_count']==6 and x['output_tokens_per_second']==20 for x in r)
def test_invalid_output_counts_false():
    r=evaluate(['a'],lambda m,t:{'raw':'not json','wall':1,'eval_count':None,'eval_duration':None})[0]
    assert r['exact_count']==0 and r['valid_count']==0 and r['output_tokens_per_second'] is None
@pytest.fixture
def client():
    with TestClient(create_app(),base_url='http://127.0.0.1:8040') as c:yield c
def test_home_and_status(client):assert client.get('/').status_code==200 and client.get('/api/status').json()['ready']
def test_model_selection(monkeypatch,client):
    monkeypatch.setattr('app.main.tags',lambda:[{'name':'m1'},{'name':'m2'}])
    assert client.post('/api/benchmark',json={'model_a':'m1','model_b':'m1'}).status_code==400
    assert client.post('/api/benchmark',json={'model_a':'m1','model_b':'not-installed'}).status_code==400
    monkeypatch.setattr('app.main.evaluate',lambda models:[{'model':x} for x in models])
    assert len(client.post('/api/benchmark',json={'model_a':'m1','model_b':'m2'}).json()['reports'])==2
def test_service_unavailable(monkeypatch,client):
    def fail():raise OllamaError('Ollama unavailable')
    monkeypatch.setattr('app.main.tags',fail)
    assert client.get('/api/models').status_code==503
def test_origin_guard(client):assert client.get('/api/status',headers={'Origin':'https://evil.example'}).status_code==403

def test_truncated_output_is_not_correct():
    c=CASES[0]
    raw=json.dumps({'category':c['category'],'priority':c['priority']})
    report=evaluate(['a'],lambda m,t:{'raw':raw,'wall':1,'eval_count':None,'eval_duration':None,'done_reason':'length'})[0]
    assert report['valid_count']==0 and report['exact_count']==0

def test_throughput_uses_paired_counters():
    i=iter(range(6))
    def fake(m,t):
        n=next(i);return {'raw':'{}','wall':1,'eval_count':20,'eval_duration':1_000_000_000 if n==0 else None}
    assert evaluate(['a'],fake)[0]['output_tokens_per_second']==20

def test_filter_common_cloud_model_tags(monkeypatch):
    from app import benchmark
    class Response:
        def raise_for_status(self): pass
        def json(self): return {'models':[{'name':'local:1b'}, {'name':'remote:cloud'}, {'name':'remote-cloud'}]}
    class Client:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def get(self,*args): return Response()
    monkeypatch.setattr(benchmark.httpx, 'Client', lambda **kwargs: Client())
    assert [m['name'] for m in benchmark.tags()] == ['local:1b']
