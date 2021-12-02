from fastapi import FastAPI, Request, File
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI()
Instrumentator().instrument(app).expose(app)


@app.get("/")
async def hello(info: Request):
    return {"Hello": "World"}


@app.post("/getInfo")
async def getInformation(info: Request):
    req_info = await info.json()
    return {"status": "SUCCESS", "data": req_info}


@app.post("/fileSize")
async def file_size(file: bytes = File(...)):
    return {"file_size": len(file)}
