import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from gateway.mcp_client import call_mcp_tool, list_all_mcp_tools

app = FastAPI(
    title="MCP Gateway",
    description="Central gateway for multiple MCP servers",
    version="0.4.0",
)

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

# Store audit records in the project directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_FILE = PROJECT_ROOT / "audit_logs.jsonl"

# Demo team keys. Set these environment variables before production use.
TEAM_API_KEYS = {
    "demo-team": os.getenv("DEMO_TEAM_API_KEY", "demo-team-key-change-me"),
    "inventory-team": os.getenv(
        "INVENTORY_TEAM_API_KEY",
        "inventory-team-key-change-me",
    ),
}


class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def authenticate(api_key: str | None) -> str:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    for team, expected_key in TEAM_API_KEYS.items():
        if secrets.compare_digest(api_key, expected_key):
            return team

    raise HTTPException(status_code=401, detail="Invalid API key")


def write_audit_log(
    team: str,
    tool_name: str,
    status: str,
    detail: str | None = None,
) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "team": team,
        "tool_name": tool_name,
        "status": status,
    }

    if detail:
        record["detail"] = detail

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


@app.get("/")
def home():
    return {
        "message": "MCP Gateway is running!",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tools")
async def list_tools():
    try:
        tools = await list_all_mcp_tools()
        return {
            "tools": tools,
            "mode": "connected",
            "server_count": 3,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/tools/execute")
async def execute_tool(
    request: ToolRequest,
    x_api_key: str | None = Header(default=None),
):
    team = authenticate(x_api_key)

    try:
        result = await call_mcp_tool(
            request.tool_name,
            request.arguments,
        )
        write_audit_log(team, request.tool_name, "success")

        return {
            "team": team,
            "tool": request.tool_name,
            "result": result,
        }

    except ValueError as exc:
        write_audit_log(
            team,
            request.tool_name,
            "failed",
            str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        write_audit_log(
            team,
            request.tool_name,
            "failed",
            str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/audit-logs")
def get_audit_logs(
    x_api_key: str | None = Header(default=None),
):
    authenticate(x_api_key)

    if not AUDIT_FILE.exists():
        return {"logs": []}

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        logs = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    return {"logs": logs[-100:]}
