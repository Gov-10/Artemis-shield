from sel import sschek 
from fastapi import FastAPI, Request
app=FastAPI()

@app.get("/health")
def chek():
    return {"status": "OK"}

@app.post("/take-ss")
def takess(request: Request):
    #TODO: Iska code shaam ko daaldunga
