# DT1 2026 :  Wit & Spark Chat Engine (Assignment 1)


GitHub username: johnmgr
Docker Hub username : budhamagarjohn
Live deployment: http://<VM_External_IP>:8501 (firewalled)

## Introduction
A containerized 3-tier LLM chat application built for university assessment. The system connects a custom **Streamlit UI frontend** to a **Flask proxy backend** that securely routes prompts to the **OpenRouter API**, deployed on a Google Cloud Platform (GCP) Virtual Machine using **Docker & Docker Compose**.

## 🏗️ System Architecture, Components & API Routes

### 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                 Client / User Network                   │
│  • University Subnet CIDR: 147.87.0.0/16                │
│  • Personal Client IP: <YOUR_PUBLIC_IP>/32              │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP Inbound (Ports 8501 & 5001)
                             ▼
┌─────────────────────────────────────────────────────────┐
│        GCP VM Host (External IP: 34.62.52.162)          │
│ 🔒 Firewall: allow-university-network (TCP 8501, 5001)  │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │          Docker Bridge Net (compose.yaml)           │ │
│ │  ┌───────────────────────────────────────────────┐  │ │
│ │  │ Streamlit UI Container (`frontend`: 8501)     │  │ │
│ │  └───────────────────────┬───────────────────────┘  │ │
│ │                          │ GET http://api:5001/chat │ │
│ │                          │ Params: model_id, token, │ │
│ │                          │         input            │ │
│ │                          ▼                          │ │
│ │  ┌───────────────────────────────────────────────┐  │ │
│ │  │ Flask API Proxy Container (`api`: 5001)       │  │ │
│ │  └───────────────────────┬───────────────────────┘  │ │
│ └──────────────────────────┼──────────────────────────┘ │
└────────────────────────────┼────────────────────────────┘
                             │ HTTPS Port 443 (Bearer Auth)
                             ▼
┌─────────────────────────────────────────────────────────┐
│      OpenRouter API Engine (openrouter.ai/api/v1)       │
│  • nvidia/nemotron-3-ultra-550b-a55b:free (Default)     │
│  • meta-llama/llama-3.3-70b-instruct:free               │
│  • google/gemma-3-27b-it:free | openai/gpt-oss-120b:free │
└─────────────────────────────────────────────────────────┘

### Markdown

🤖 [ Integrated LLM Engines & Status ]

• nvidia/nemotron-3-ultra-550b-a55b:free ── [🟢 Active / Primary]

• meta-llama/llama-3.3-70b-instruct:free  ── [🛠️ Troubleshooting Mode]
• google/gemma-3-27b-it:free             ── [🛠️ Troubleshooting Mode]
• openai/gpt-oss-120b:free               ── [🛠️ Troubleshooting Mode]

```

### Components Breakdown

* **Frontend UI (`frontend`):** Built with Streamlit running on port `8501`. Handles chat interface rendering, interactive model switching, real-time backend health diagnostics, execution latency tracking, and chat session state memory.
* **Middleware Proxy (`api`):** Built with Flask running on port `5001`. Acts as a controlled proxy to handle URL parameter extraction, inject authentication credentials, enforce CORS headers, and communicate with external LLM engines.
* **External Gateway (`OpenRouter API`):** External LLM provider endpoint managing bearer token authorization and returning completion payloads from open-weights language models.

### Data Flow

1. **User Request:** User navigates to `http://34.62.52.162:8501` and submits a chat prompt.
2. **Frontend Dispatch:** Streamlit URL-encodes request parameters (`model_id`, `openrouter_token`, `input`) and dispatches an HTTP GET request across the Docker bridge network to `http://api:5001/chat`.
3. **Backend Processing:** Flask extracts query parameters, formats an OpenRouter payload, attaches the Bearer token, and executes an HTTPS request over port 443.
4. **LLM Response:** OpenRouter returns the generated AI response to Flask, which packages it into JSON (`{"ack": "<AI_RESPONSE>"}`) and passes it back to Streamlit for rendering.

### API Routes

| Endpoint | Method | Source $\rightarrow$ Target | Purpose & Payload |
| :--- | :--- | :--- | :--- |
| `/ping` | `GET` | Streamlit $\rightarrow$ Flask Proxy | Diagnostics check. Returns `{"status": "ok"}` with HTTP status `200`. |
| `/chat` | `GET` | Streamlit $\rightarrow$ Flask Proxy | Core chat route. Accepts parameters `model_id`, `openrouter_token`, and `input`. Returns `{"ack": "<RESPONSE_TEXT>"}`. |

---

## 🚀 Google Cloud VM Deployment Steps

### 1. Connect and Clone
SSH into GCP VM instance (`34.62.52.162`) and clone the repository:
```bash
git clone https://github.com/johnmgr/budhamagar_john-dt1-26.git
cd budhamagar_john-dt1-26
```

### 2. Configure Secret Keys
Create the `.env` secret file in the project root directory:
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key" > .env
```

### 3. Setup GCP Firewall Ingress
In GCP Console (**VPC Network $\rightarrow$ Firewall**), create an ingress rule named `allow-university-network`:
* **Direction:** Ingress
* **Action:** Allow
* **Target:** All instances in network
* **Protocols & Ports:** Specified TCP `8501`, `5001`
* **Source IP Ranges:** `147.87.0.0/16` (University Subnet) and `<MY_IP>/32`

### 4. Build and Run Container Stack
Build and start both container services in the background using Docker Compose:
```bash
sudo docker compose up --build -d
```

### 5. Verify Endpoints
* **Frontend Web UI:** Access `http://34.62.52.162:8501`
* **Backend Health Check:** Access `http://34.62.52.162:5001/ping`

---

## ✏️ Changes Made to Original Codebase (isnpired by github username: houssemgharbi666-sys)

### 1. Frontend (`frontend.py`)
* **Real-time Health Badge:** Added background `/ping` health checks to render a live connection status (`Online 🟢` vs `Unreachable 🔴`) in the sidebar.
* **Model Dropdown Switcher:** Implemented dynamic selection across free-tier OpenRouter models (`nvidia`, `llama`, `gemma`, `gpt-oss`).
* **Latency Tracker:** Added timer metrics calculating and displaying response execution time in seconds under each response.
* **Clear Chat Action:** Added a button to clear conversation history (`st.session_state`) without requiring a browser reload.

### 2. Backend Proxy (`api.py`)
* **GET Routing Logic:** Adapted `/chat` endpoint to parse URL-encoded query strings (`model_id`, `openrouter_token`, `input`).
* **Cross-Origin Resource Sharing:** Enabled `flask_cors.CORS` to handle internal container requests.

### 3. Container & Build Setup (`compose.yaml` & `Dockerfile.api`)
* **Service Linking:** Configured internal container bridge networking using service hostnames (`http://api:5001`).
* **Lightweight Base Image:** Switched container builds to `python:3.13-alpine` for minimal memory footprint and faster build times.
* **Startup Ordering:** Configured `depends_on` to ensure Flask API initializes prior to Streamlit.

### 4. Security (`.gitignore`)
* Configured `.gitignore` to prevent secret API keys (`.env`), virtual environments (`.venv`), and local draft notes (`ROADME.local.md`) from being committed to Git.

