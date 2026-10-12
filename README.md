## Demo Video

Watch the project walkthrough here:

[Urumi AI FDE Internship — MCP Gateway Demo Video](https://drive.google.com/file/d/1p03TPzjpcShRgZVUtP5F1ly7Y-PVBWcQ/view?usp=sharing)

# MCP Gateway on Kubernetes

A Kubernetes-deployed MCP Gateway that connects multiple Model Context Protocol (MCP) servers and provides a centralized interface for discovering tools, interacting with an AI agent, and monitoring tool usage.

## Project Overview

This project demonstrates how multiple MCP servers can be connected through a central gateway and accessed through a React dashboard and an AI agent.

## Architecture

- **WooCommerce MCP Server:** Provides demo store tools for products and orders.
- **Inventory MCP Server:** Provides inventory and stock-checking tools.
- **Shipping MCP Server:** Provides shipment and order-tracking tools.
- **MCP Gateway:** Connects MCP servers, exposes tools, authenticates requests, and records audit logs.
- **AI Agent:** Sends user requests to the gateway and presents tool results.
- **React Dashboard:** Displays gateway connectivity, available tools, and chat interactions.
- **Docker:** Packages the application components into container images.
- **Kubernetes and Helm:** Deploy and manage the application components.

## Features

- Integration of three MCP servers through a centralized gateway.
- Tool discovery and execution.
- Product lookup and order queries using demo store data.
- Inventory and stock-checking operations.
- Shipment tracking.
- API-key-based access control.
- Audit logging of tool activity.
- React-based dashboard and chat interface.
- Kubernetes deployment using Helm.
- Health-check endpoints for the gateway and agent.

## Technology Stack

- Python
- FastAPI
- Model Context Protocol (MCP)
- React
- Vite
- Docker
- Kubernetes
- Helm
- kind (Kubernetes in Docker)
- PowerShell

## Project Structure

```text
mcp-gateway-project/
├── agent/
├── dashboard/
├── gateway/
├── inventory-mcp-server/
├── shipping-mcp-server/
├── woo-mcp-server/
├── k8s/
├── mcp-gateway-chart/
├── Dockerfile.agent
├── Dockerfile.dashboard
├── Dockerfile.gateway
├── requirements.txt
├── audit_logs.jsonl
└── README.md
```

## Prerequisites

Install the following tools before running the project:

- Python 3.12
- Node.js and npm
- Docker Desktop
- kubectl
- kind
- Helm
- Visual Studio Code (recommended)

## Local Setup

Open PowerShell in the project root.

### 1. Create and activate a Python virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Prepare the dashboard

```powershell
cd dashboard
npm install
cd ..
```

## Kubernetes Deployment

Make sure Docker Desktop is running and the kind cluster is available.

### 1. Check the cluster

```powershell
kubectl cluster-info
kubectl get nodes
```

### 2. Validate the Helm chart

```powershell
helm lint .\mcp-gateway-chart
helm template mcp-gateway .\mcp-gateway-chart
```

### 3. Install or upgrade the application

For a first-time installation:

```powershell
helm install mcp-gateway .\mcp-gateway-chart
```

For an existing installation:

```powershell
helm upgrade mcp-gateway .\mcp-gateway-chart
```

### 4. Verify the deployment

```powershell
kubectl get pods
kubectl get services
helm test mcp-gateway
```

All application pods should reach the Running state before testing the application.

## Access the Dashboard

Forward the dashboard service to your local machine:

```powershell
kubectl port-forward service/dashboard 5173:80
```

Open the following address in your browser:

http://localhost:5173

Keep the PowerShell terminal running while using the port-forward connection.

## Health Checks

Forward the gateway and agent services in separate terminals if they are not already accessible locally.

Example commands:

```powershell
kubectl port-forward service/gateway 8000:8000
```

```powershell
kubectl port-forward service/agent 8001:8001
```

Check their health endpoints:

- Gateway: http://127.0.0.1:8000/health
- Agent: http://127.0.0.1:8001/health

## Example Interaction

Example user request:

`Track order 1001`

The demo agent can return the order's tracking identifier, shipping status, and estimated delivery information using the configured demo data.

Other example requests include product searches and inventory stock checks.

## Audit Logging and Security

The gateway records tool activity in `audit_logs.jsonl` for auditing and troubleshooting.

The project includes API-key-based access control. For any real deployment, replace demo keys with secure environment-based secrets, avoid committing credentials, and configure appropriate access controls.

## Current Limitations

The WooCommerce MCP server currently uses demo/static store data. A live WooCommerce store integration requires configuring the WooCommerce API credentials and implementing or verifying the corresponding live API calls.

The AI agent's behavior should also be described according to its actual implementation; a rule-based agent should not be represented as an autonomous LLM agent.

## Future Improvements

- Integrate a live WooCommerce store.
- Store API keys securely using Kubernetes Secrets.
- Add richer audit-log filtering and monitoring.
- Improve automated tests and error handling.
- Expand the AI agent's natural-language tool selection.

## Author

**Charishma Akuthota**

GitHub: https://github.com/Charishma12301/

LinkedIn: https://www.linkedin.com/in/akuthota-charishma-344a99293/
