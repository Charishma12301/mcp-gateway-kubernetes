from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Shipping MCP Server")

SHIPMENTS = [
    {"order_id": 1001, "tracking_id": "TRK1001", "status": "shipped", "estimated_delivery": "2026-10-13"},
    {"order_id": 1002, "tracking_id": "TRK1002", "status": "in_transit", "estimated_delivery": "2026-10-12"},
    {"order_id": 1003, "tracking_id": "TRK1003", "status": "processing", "estimated_delivery": "2026-10-15"},
]


@mcp.tool()
def list_shipments() -> list:
    """List all demo shipments."""
    return SHIPMENTS


@mcp.tool()
def track_order(order_id: int) -> dict:
    """Get shipping and tracking information for an order."""
    for shipment in SHIPMENTS:
        if shipment["order_id"] == order_id:
            return shipment
    return {"error": f"Shipment for order {order_id} not found"}


if __name__ == "__main__":
    mcp.run()
