from pydantic import BaseModel, Field
from datetime import datetime, timezone
import platform
from fastapi import HTTPException
from app.base import create_base
from app.benchmark import tags,evaluate,CASES,OllamaError,SYSTEM

class Selection(BaseModel):
    model_a:str=Field(min_length=1,max_length=200)
    model_b:str=Field(min_length=1,max_length=200)

def create_app():
    app=create_base('LocalLLMLab')
    @app.get('/api/status')
    def status():return {'ready':True,'dataset':'6 fictional support requests','provider':'Local Ollama'}
    @app.get('/api/examples')
    def examples():return {'cases':CASES}
    @app.get('/api/models')
    def models():
        try:return {'models':tags()}
        except OllamaError as e:raise HTTPException(503,str(e)) from e
    @app.post('/api/benchmark')
    def benchmark(body:Selection):
        if body.model_a==body.model_b:raise HTTPException(400,'Choose two different installed model tags.')
        try:
            metadata=tags();available={x['name'] for x in metadata}
            if not {body.model_a,body.model_b}.issubset(available):raise HTTPException(400,'Both model tags must be installed in the local Ollama instance.')
            return {'reports':evaluate([body.model_a,body.model_b]), 'configuration':{'timestamp_utc':datetime.now(timezone.utc).isoformat(),'model_metadata':[x for x in metadata if x['name'] in (body.model_a,body.model_b)],'system_prompt':SYSTEM,'options':{'temperature':0,'seed':42,'num_predict':128},'platform':platform.platform(),'python':platform.python_version()},'caveat':'Six synthetic examples; one run per model; order and cold starts can affect timing.'}
        except OllamaError as e:raise HTTPException(502,str(e)) from e
    return app
app=create_app()
