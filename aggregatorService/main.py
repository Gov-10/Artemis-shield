from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def chek():
    return {"status": "OK"}
