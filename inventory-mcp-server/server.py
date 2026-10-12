from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Inventory MCP Server")

INVENTORY = [
    {"product_id": 1, "name": "Wireless Mouse", "quantity": 25},
    {"product_id": 2, "name": "Mechanical Keyboard", "quantity": 10},
    {"product_id": 3, "name": "USB-C Hub", "quantity": 15},
]

@mcp.tool()
def list_inventory() -> list:
    """List inventory quantities for all products."""
    return INVENTORY

@mcp.tool()
def check_stock(product_id: int) -> dict:
    """Check inventory quantity for a product ID."""
    for item in INVENTORY:
        if item["product_id"] == product_id:
            return item
    return {"error": f"Product {product_id} not found"}

if __name__ == "__main__":
    mcp.run()
