from google.cloud import pubsub_v1
from ninja import NinjaAPI, Schema
import os
from dotenv import load_dotenv
load_dotenv()
credentials_path = os.getenv("cred")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
publisher = pubsub_v1.PublisherClient()
topic_path = os.getenv("INPUT_TOPIC")
api = NinjaAPI()
import json
import uuid


class InputSchema(Schema):
    url:str

@api.get("/health")
def chek(request):
    return {"status": "OK"}
@api.post("/analyse")
def ana(request, payload:InputSchema):
    url=payload.url
    id1 =str(uuid.uuid4())
    dt={"url":url, "id":id1}
    data=json.dumps(dt).encode("utf-8")
    pu=publisher.publish(topic_path, data)
    return {"publishId":pu}
    