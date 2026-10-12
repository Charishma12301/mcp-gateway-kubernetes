
import { useEffect, useState } from "react";
import "./App.css";

const GATEWAY = "http://127.0.0.1:8000";
const AGENT = "http://127.0.0.1:8001";

function normalizeResult(result) {
  if (!Array.isArray(result)) {
    return result;
  }

  const normalized = [];

  for (const item of result) {
    let value = item;

    if (item && typeof item === "object" && typeof item.text === "string") {
      try {
        value = JSON.parse(item.text);
      } catch {
        value = item.text;
      }
    }

    if (typeof value === "string") {
      try {
        value = JSON.parse(value);
      } catch {
        // Keep ordinary text unchanged.
      }
    }

    if (Array.isArray(value)) {
      normalized.push(...value);
    } else {
      normalized.push(value);
    }
  }

  return normalized;
}

function formatResponse(data) {
  if (!data.tool_used) {
    return data.reply || "No response returned.";
  }

  const result = normalizeResult(data.result);
  const tool = data.tool_used;

  if (tool === "list_products" || tool === "search_products") {
    const products = Array.isArray(result) ? result : [result];

    if (products.length === 0) {
      return "No products found.";
    }

    return (
      `Products (${products.length})\n\n` +
      products
        .map((product, index) => {
          if (!product || typeof product !== "object") {
            return String(product);
          }

          return (
            `${index + 1}. ${product.name || "Unnamed product"}\n` +
            `   Product ID: ${product.id ?? "N/A"}\n` +
            `   Price: ${product.price != null ? `₹${product.price}` : "N/A"}\n` +
            `   Stock: ${product.stock ?? "N/A"}`
          );
        })
        .join("\n\n")
    );
  }

  if (tool === "get_product") {
    const product = Array.isArray(result) ? result[0] : result;

    if (product?.error) return product.error;

    if (product && typeof product === "object") {
      return (
        `Product Details\n\n` +
        `Name: ${product.name ?? "N/A"}\n` +
        `Product ID: ${product.id ?? "N/A"}\n` +
        `Price: ${product.price != null ? `₹${product.price}` : "N/A"}\n` +
        `Stock: ${product.stock ?? "N/A"}`
      );
    }
  }

  if (tool === "check_stock" || tool === "list_inventory") {
    const items = Array.isArray(result) ? result : [result];

    return (
      `Inventory Details\n\n` +
      items
        .map((item) => {
          if (!item || typeof item !== "object") return String(item);
          if (item.error) return item.error;

          return (
            `Product: ${item.name ?? "N/A"}\n` +
            `Product ID: ${item.product_id ?? "N/A"}\n` +
            `Available Quantity: ${item.quantity ?? "N/A"}`
          );
        })
        .join("\n\n")
    );
  }

  if (tool === "track_order" || tool === "get_order") {
    const order = Array.isArray(result) ? result[0] : result;

    if (order?.error) return order.error;

    if (order && typeof order === "object") {
      return (
        `${tool === "track_order" ? "Order Tracking" : "Order Details"}\n\n` +
        `Order ID: ${order.order_id ?? order.id ?? "N/A"}\n` +
        (order.tracking_id ? `Tracking ID: ${order.tracking_id}\n` : "") +
        `Status: ${order.status ?? "N/A"}\n` +
        (order.estimated_delivery
          ? `Estimated Delivery: ${order.estimated_delivery}\n`
          : "") +
        (order.total != null ? `Total: ₹${order.total}` : "")
      ).trim();
    }
  }

  if (tool === "list_shipments" || tool === "list_orders") {
    const items = Array.isArray(result) ? result : [result];

    return (
      `${tool === "list_shipments" ? "Shipments" : "Orders"}\n\n` +
      items
        .map((item, index) => {
          if (!item || typeof item !== "object") return String(item);

          return (
            `${index + 1}. ID: ${item.order_id ?? item.id ?? "N/A"}\n` +
            (item.tracking_id ? `   Tracking: ${item.tracking_id}\n` : "") +
            `   Status: ${item.status ?? "N/A"}\n` +
            (item.estimated_delivery
              ? `   Estimated Delivery: ${item.estimated_delivery}\n`
              : "") +
            (item.total != null ? `   Total: ₹${item.total}` : "")
          ).trim();
        })
        .join("\n\n")
    );
  }

  if (tool === "get_store_status") {
    const status = Array.isArray(result) ? result[0] : result;

    if (status && typeof status === "object") {
      return (
        `Store Status\n\n` +
        `Store: ${status.store ?? "N/A"}\n` +
        `Status: ${status.status ?? "N/A"}\n` +
        `Mode: ${status.mode ?? "N/A"}`
      );
    }
  }

  return `Tool: ${tool}\n\n${JSON.stringify(result, null, 2)}`;
}

export default function App() {
  const [health, setHealth] = useState("Checking...");
  const [tools, setTools] = useState([]);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function loadDashboard() {
    setRefreshing(true);

    try {
      const [healthResponse, toolsResponse] = await Promise.all([
        fetch(`${GATEWAY}/health`),
        fetch(`${GATEWAY}/tools`),
      ]);

      if (!healthResponse.ok || !toolsResponse.ok) {
        throw new Error("Gateway request failed");
      }

      const healthData = await healthResponse.json();
      const toolsData = await toolsResponse.json();

      setHealth(
        healthData.status === "ok" ? "Connected" : "Unavailable"
      );
      setTools(toolsData.tools || []);
    } catch {
      setHealth("Unavailable");
      setTools([]);
    } finally {
      setRefreshing(false);
    }
  }

  async function sendMessage(event) {
    event.preventDefault();

    if (!message.trim() || loading) return;

    const userMessage = message.trim();

    setChat((previous) => [
      ...previous,
      { role: "user", text: userMessage },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${AGENT}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Chat request failed");
      }

      setChat((previous) => [
        ...previous,
        {
          role: "assistant",
          text: formatResponse(data),
        },
      ]);
    } catch (error) {
      setChat((previous) => [
        ...previous,
        {
          role: "assistant",
          text: `Error: ${error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  return (
    <main className="dashboard">
      <header className="topbar">
        <div>
          <p className="eyebrow">MCP PLATFORM</p>
          <h1>MCP Gateway Dashboard</h1>
          <p className="subtitle">
            Manage connected tools and test your chat agent.
          </p>
        </div>

        <button
          className="refresh"
          onClick={loadDashboard}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing..." : "Refresh status"}
        </button>
      </header>

      <section className="stats">
        <article className="stat-card">
          <span>Gateway</span>
          <h2 className={health === "Connected" ? "online" : "offline"}>
            {health}
          </h2>
          <p>127.0.0.1:8000</p>
        </article>

        <article className="stat-card">
          <span>Discovered tools</span>
          <h2>{tools.length}</h2>
          <p>Across 3 MCP servers</p>
        </article>

        <article className="stat-card">
          <span>Chat agent</span>
          <h2>Port 8001</h2>
          <p>Rule-based prototype</p>
        </article>
      </section>

      <section className="content-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <h2>Available tools</h2>
              <p>Tools discovered through the gateway</p>
            </div>
            <span className="count">{tools.length}</span>
          </div>

          {tools.length === 0 ? (
            <p className="empty">
              No tools loaded. Check that the gateway is running.
            </p>
          ) : (
            <div className="tool-list">
              {tools.map((tool) => (
                <div
                  className="tool-row"
                  key={`${tool.server}-${tool.name}`}
                >
                  <div className="tool-icon">⚙</div>

                  <div className="tool-info">
                    <strong>{tool.name}</strong>
                    <p>{tool.description || "No description available"}</p>
                  </div>

                  <span className="server-tag">{tool.server}</span>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="panel chat-panel">
          <div className="panel-heading">
            <div>
              <h2>Chat with your store</h2>
              <p>Ask about products, stock, or orders</p>
            </div>
          </div>

          <div className="chat-messages">
            {chat.length === 0 && (
              <div className="welcome">
                <div className="welcome-icon">✦</div>
                <h3>How can I help?</h3>
                <p>Try asking:</p>
                <p>• Show all products</p>
                <p>• Check stock for product 3</p>
                <p>• Track order 1001</p>
              </div>
            )}

            {chat.map((item, index) => (
              <div
                className={`chat-bubble ${item.role}`}
                key={`${item.role}-${index}`}
              >
                <span>{item.role === "user" ? "You" : "Agent"}</span>
                <pre>{item.text}</pre>
              </div>
            ))}

            {loading && (
              <p className="loading">Agent is working...</p>
            )}
          </div>

          <form className="chat-form" onSubmit={sendMessage}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask about products or orders..."
              aria-label="Chat message"
              disabled={loading}
            />

            <button
              type="submit"
              disabled={loading || !message.trim()}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
        </article>
      </section>

      <footer>MCP Gateway · Local development environment</footer>
    </main>
  );
}
