import os
import time
from urllib.parse import quote
import requests
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="AI Quick Wit & Short Chat",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for a cleaner modern look (rounded corners, subtle shadows, badges)
st.markdown(
    """
    <style>
    .stChatInputContainer {
        padding-bottom: 10px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 10px 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Available models for selection
MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai/gpt-oss-120b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
]

# Environment variables & Host setup
HOST = os.getenv("BASE_URL", "http://api:5001").rstrip("/")
ENV_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Initialize Session States for Chat History
st.session_state.setdefault("history", [])
st.session_state.setdefault("prompt", "")


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def check_backend_health() -> bool:
  """Quickly pings the Flask backend /ping route to check connection status."""
  try:
    res = requests.get(f"{HOST}/ping", timeout=2)
    return res.status_code == 200
  except requests.RequestException:
    return False


def handle_send():
  """Handles request dispatching using the instructor's GET route specification."""
  text = st.session_state.prompt.strip()
  if not text:
    return

  # Reset input state box
  st.session_state.prompt = ""

  # Resolve token source (Sidebar override or Environment Variable)
  active_key = st.session_state.get("key_override", "").strip() or ENV_KEY
  selected_model = st.session_state.get("model_selector", MODELS[0])

  # URL Encode Parameters to prevent syntax/escaping bugs
  model_enc = quote(selected_model)
  token_enc = quote(active_key)
  input_enc = quote(text)

  # Construct the precise GET endpoint requested by the backend spec
  endpoint = (
      f"{HOST}/chat?model_id={model_enc}&"
      f"openrouter_token={token_enc}&"
      f"input={input_enc}"
  )

  start_time = time.time()
  reply_content = ""
  is_success = False

  try:
    with st.spinner("✨ Crafting a short & funny response..."):
      response = requests.get(endpoint, timeout=120)
      body = response.json() if response.content else {}

      if response.status_code == 200:
        reply_content = body.get("ack", "No acknowledgement found.")
        is_success = True
      else:
        reply_content = f"Error [{response.status_code}]: {body.get('error', response.text)}"
        is_success = False

  except requests.exceptions.RequestException as connection_error:
    reply_content = f"Connection failure to API proxy: {connection_error}"
    is_success = False

  elapsed_time = time.time() - start_time

  # Prepend new interaction into history stack
  st.session_state.history.insert(
      0,
      {
          "query": text,
          "response": reply_content,
          "status": is_success,
          "model": selected_model,
          "latency": elapsed_time,
      },
  )


# ==========================================
# 3. SIDEBAR CONTROLS & DASHBOARD
# ==========================================
with st.sidebar:
  st.markdown("### 🎛️ Control Panel")
  st.selectbox(
      "Choose LLM Engine", MODELS, key="model_selector", help="Select model."
  )

  st.text_input(
      "API Key Override",
      type="password",
      key="key_override",
      placeholder="Optional override...",
  )

  st.divider()

  # Backend Status Widget Display
  st.markdown("### 🔌 System Diagnostics")
  if check_backend_health():
    st.success("Flask Backend: **Online 🟢**")
  else:
    st.error("Flask Backend: **Unreachable 🔴**")

  st.divider()

  # Action Buttons
  if st.button("🧹 Clear Chat Feed", use_container_width=True):
    st.session_state.history = []
    st.rerun()

  st.markdown(
      "<small style='color: grey;'>Built with Streamlit & Flask Proxy</small>",
      unsafe_allow_html=True,
  )


# ==========================================
# 4. MAIN USER INTERFACE HEADER
# ==========================================
st.markdown(
    """
    <div style='padding: 10px 0px;'>
        <h2>⚡ Wit & Spark Chat Engine</h2>
        <p style='color: #6c757d;'>A streamlined UI interfacing seamlessly via proxy to OpenRouter API.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Text Area Input Component
st.text_area(
    "What's on your mind?",
    key="prompt",
    height=90,
    placeholder="e.g., Tell me a short and witty joke about debugging.",
)

# Primary Interaction Trigger Button
st.button("🚀 Send Prompt", type="primary", on_click=handle_send)

st.divider()

# ==========================================
# 5. CHAT FEED LOGIC & BUBBLES
# ==========================================
if not st.session_state.history:
  st.info("💡 Tip: Type a prompt above and click **Send Prompt** to begin!")

for message_item in st.session_state.history:
  # User message container
  with st.chat_message("user", avatar="👤"):
    st.markdown(message_item["query"])

  # Assistant message container
  with st.chat_message("assistant", avatar="⚡"):
    if message_item["status"]:
      st.markdown(message_item["response"])
    else:
      st.error(message_item["response"])

    # Metadata caption showing model footprint and execution timing
    st.caption(
        f"Model: `{message_item['model'].split('/')[1]}` • ⏱️"
        f" {message_item['latency']:.2f}s"
    )
# Add additional endpoints/buttons as needed when system works
