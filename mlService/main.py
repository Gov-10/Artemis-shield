from fastapi import FastAPI, Request
from predict import predict_vibe1
from google.cloud import pubsub_v1
app=FastAPI()
from dotenv import load_dotenv
import os, json
credentials_path=os.getenv("cred")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=credentials_path
import base64
publisher=pubsub_v1.PublisherClient()
ML_PATH=os.getenv("ML_TOPIC")
load_dotenv()
@app.get("/health")
def chek():
    return {"status": "OK"}

@api.post("/ml")
async def pred(request: Request):
    try:
        body = await request.json()
        message=body.get("message", {})
        data=message.get("data")
        if not data:
            return {"status": "no data"}
        dcd=base64.b64decode(data).decode("utf-8")
        payload=json.loads(dcd)
        url,id1=payload.get("url"), payload.get("id1")
        verdict,phish_prob=predict_vibe1(url)
        data={"id1": id1, "url":url, "verdict": verdict, "phish_prob": phish_prob}
        dt=json.dumps(data).encode("utf-8")
        pu=publisher.publish(ML_PATH, dt)
        return {"status": f"published: {pu.result()}"}
    except Exception as e:
        print(f"error: {str(e)}")
        return {"status": "FAILED"}



