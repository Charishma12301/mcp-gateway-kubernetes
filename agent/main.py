import os
import re

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MCP Chat Agent")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")

# Must match the demo key configured in gateway/main.py
GATEWAY_API_KEY = "demo-team-key-change-me"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "MCP Chat Agent is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.lower().strip()

    if "product" in message and not any(
        word in message for word in ["stock", "inventory"]
    ):
        tool_name = "list_products"
        arguments = {}

    elif "stock" in message or "inventory" in message:
        tool_name = "check_stock"
        arguments = {"product_id": extract_id(message, 2)}

    elif any(
        word in message
        for word in ["track", "shipment", "order"]
    ):
        tool_name = "track_order"
        arguments = {"order_id": extract_id(message, 1001)}

    else:
        return {
            "reply": (
                "Try asking about products, stock, "
                "or tracking an order."
            )
        }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{GATEWAY_URL}/tools/execute",
                headers={
                    "X-API-Key": GATEWAY_API_KEY,
                },
                json={
                    "tool_name": tool_name,
                    "arguments": arguments,
                },
            )

            response.raise_for_status()
            data = response.json()

        return {
            "message": request.message,
            "team": data.get("team"),
            "tool_used": data.get("tool"),
            "result": data.get("result"),
        }

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Gateway error: {exc.response.text}",
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gateway request failed: {exc}",
        ) from exc


def extract_id(message: str, default_id: int) -> int:
    match = re.search(r"\b\d+\b", message)
    return int(match.group()) if match else default_id
