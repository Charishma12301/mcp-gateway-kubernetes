
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MCP_SERVERS = {
    "woo": PROJECT_ROOT / "woo-mcp-server" / "server.py",
    "inventory": PROJECT_ROOT / "inventory-mcp-server" / "server.py",
    "shipping": PROJECT_ROOT / "shipping-mcp-server" / "server.py",
}

async def list_all_mcp_tools() -> list[dict[str, str]]:
    all_tools = []

    for server_name, server_file in MCP_SERVERS.items():
        if not server_file.exists():
            raise FileNotFoundError(f"MCP server not found: {server_file}")

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_file)],
            env=os.environ.copy(),
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()

                for tool in response.tools:
                    all_tools.append({
                        "name": tool.name,
                        "description": tool.description or "",
                        "server": server_name,
                    })

    return all_tools


async def call_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> Any:
    for server_name, server_file in MCP_SERVERS.items():
        if not server_file.exists():
            raise FileNotFoundError(f"MCP server not found: {server_file}")

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_file)],
            env=os.environ.copy(),
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()

                tool_names = {tool.name for tool in response.tools}

                if tool_name not in tool_names:
                    continue

                result = await session.call_tool(
                    tool_name,
                    arguments=arguments or {},
                )

                if result.isError:
                    raise RuntimeError(f"MCP tool '{tool_name}' failed")

                return [
                    item.model_dump(mode="json")
                    for item in result.content
                ]

    raise ValueError(f"Unknown MCP tool: {tool_name}")
