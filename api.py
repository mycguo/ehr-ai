from fastapi import FastAPI, Request
from langgraph.billing_graph import build_graph

app = FastAPI()
graph = build_graph()

@app.post("/generate-claim")
async def generate_claim(request: Request):
    body = await request.json()
    result = graph.invoke({
        "soap_note": body["soap_note"]
    })
    return result
