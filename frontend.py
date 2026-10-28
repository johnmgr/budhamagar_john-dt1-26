import streamlit as st
import requests
import os
from urllib.parse import quote

st.title("A Simple Short and Funny Chat System")

# 1. Handle API credentials and base host for Docker service communication/Initialize OpenRouter API token from environment variables
if "openrouter_api_token" not in st.session_state:
    st.session_state.openrouter_api_token = os.getenv("OPENROUTER_API_KEY")

 # Initialize host/base URL with a fallback to the Docker service name 'api' if BASE_URL isn't in .env
if "host" not in st.session_state:
 # Defaults to the Docker Compose service name 'api' on port 5001
  st.session_state.host = os.getenv("BASE_URL", "http://api:5001")

# 2. Capture user input/User prompt input element matching the requirements
user_input = st.text_input("Ask me something", placeholder = "e.g.,hello")
user_input_encode = quote(user_input)

# 3. Specify the required model ID/Required model ID specified
model_id = "nvidia/nemotron-3-ultra-550b-a55b:free"
model_id_encode = quote(model_id)

# Optional: Display the selected model for clarity
st.caption(f"Using Model: `{model_id}`")

# 4. Construct and send the API query when the button is clicked/this is the button and the action that it takes when it is clicked
if st.button("chat"):
  if not user_input.strip():
   st.warning("Please enter a prompt before clicking chat.")
  elif not st.session_state.openrouter_api_token:
    st.error(
        "OpenRouter API Key is missing! Check your .env file or environment"
        " configuration."
    )
  else
    # Build the endpoint URL matching GET request pattern/Target /chat route with the correct query parameters
    ENDPOINT = (
        f"{st.session_state.host}/chat?model_id={model_id_encode}&"
        f"openrouter_token={st.session_state.openrouter_api_token}&"
        f"input={user_input_encode}"
    )

    with st.spinner(f"Calling {model_id}..."):
     try:
       response = requests.get(ENDPOINT, timeout=120)
        if response.status_code == 200:
            st.success("Success!")
           # Displays the "ack" response returned from Flask api.py/ the backend
            st.write(response.json().get("ack"))
        else:
            st.error(
                f"Failed with status code {response.status_code}:"
                f" {response.text}"
         )
   except requests.exceptions.RequestException as e:
     st.error(f"Connection error to backend proxy: {e}")

# Add additional endpoints/buttons as needed when system works
