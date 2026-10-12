from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WooCommerce MCP Server")

PRODUCTS = [
    {"id": 1, "name": "Wireless Mouse", "price": 799.00, "stock": 25},
    {"id": 2, "name": "Mechanical Keyboard", "price": 2499.00, "stock": 10},
    {"id": 3, "name": "USB-C Hub", "price": 1499.00, "stock": 15},
]

ORDERS = [
    {"id": 1001, "customer": "Customer A", "status": "processing", "total": 799.00},
    {"id": 1002, "customer": "Customer B", "status": "completed", "total": 2499.00},
]

@mcp.tool()
def get_store_status() -> dict:
    """Check the status of the demo store."""
    return {"store": "WooCommerce", "status": "connected", "mode": "demo"}

@mcp.tool()
def list_products() -> list:
    """Return all demo products."""
    return PRODUCTS

@mcp.tool()
def get_product(product_id: int) -> dict:
    """Get a product by ID."""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return {"error": f"Product {product_id} not found"}

@mcp.tool()
def search_products(keyword: str) -> list:
    """Search products by name."""
    keyword = keyword.lower().strip()
    return [p for p in PRODUCTS if keyword in p["name"].lower()]

@mcp.tool()
def list_orders() -> list:
    """Return demo orders."""
    return ORDERS

@mcp.tool()
def get_order(order_id: int) -> dict:
    """Get an order by ID."""
    for order in ORDERS:
        if order["id"] == order_id:
            return order
    return {"error": f"Order {order_id} not found"}

if __name__ == "__main__":
    mcp.run()
