# ==============================================================================
# 🍽️ THE RESTAURANT ANALOGY: Flask API Backend (`api.py`)
# ------------------------------------------------------------------------------
# Imagine this file as a Middleman Proxy Restaurant:
# - Streamlit Frontend = The Customer sitting at the dining table
# - Flask Proxy (`api.py`) = The Waiter taking order tickets and serving dishes
# - OpenRouter API = The Supplier Kitchen with specialized AI Chefs
# ==============================================================================

# 1. IMPORTING OUR SUPPLIES & TOOLS
# We bring in our essential restaurant gear:
from flask import Flask, request as req, jsonify  # Flask = The restaurant building; req = Order pad; jsonify = Plating food neatly into JSON boxes
from openai import OpenAI                         # OpenAI Client = The hotline phone to call external supplier kitchens
import logging                                     # Logging = The manager's notepad to write down orders for debugging
import os                                          # OS = Environment inspector (reads environment variables like PORT)

# 2. OPENING THE RESTAURANT
# Initialize the Flask app. Think of this as officially hanging the "OPEN" sign on our door!
app = Flask(__name__)


# 3. THE KITCHEN SUPPLIER ROUTINE (Head Chef Helper)
# This function handles dialing OpenRouter, passing the customer's ticket, and receiving the cooked meal.
def query(payload, model_id, api_token):
    # Establish a phone call connection to OpenRouter's master kitchen network
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",  # The street address of OpenRouter's kitchen
        api_key=api_token,                        # The customer's VIP payment ticket / API key
    )

    # Request the specific AI Chef (e.g., Nvidia Nemotron) to prepare the response
    response = client.chat.completions.create(
        model=model_id,                           # Which specialized AI chef should prepare this order?
        messages=[
            {
                "role": "user",
                "content": payload["input"],      # The customer's raw prompt / recipe request
            }
        ],
        extra_body={"reasoning": {"enabled": True}}, # Telling the kitchen: "Take a moment to think carefully before answering"
    )

    return response  # Return the freshly cooked response payload back to the waiter


# 4. COUNTER #1: THE CHAT ORDER STATION (`/chat` route)
# When a customer sends a request to 'http://<VM_IP>:5001/chat', this waiter steps up to process the order.
@app.route("/chat", methods=["GET"])
def call_openrouter_chat_model():
    # A. Reading the customer's order ticket (URL Query Parameters)
    model_id = req.args.get("model_id")                     # Waiter reads: "Which AI model did you pick?"
    logging.debug(f"The model ID for the openrouter model is {model_id}")
    
    openrouter_token = req.args.get("openrouter_token")     # Waiter reads: "May I see your OpenRouter API token?"
    logging.debug(f"openrouter API Token: {openrouter_token}")
    
    questions = req.args.get("input")                        # Waiter reads: "What is your prompt question?"
    
    # B. Dispatching the order to the kitchen helper function
    data = query(
        {"input": f"{questions}"},
        model_id,
        openrouter_token,
    )
    logging.debug(f"Model output: {data}")
    
    # C. Plating the dish neatly
    # We extract the text output from the first response choice and pack it into a JSON key named "ack"
    output = jsonify({"ack": data.choices[0].message.content})
    
    # D. Adding a "Welcome Everyone" sign (CORS Header)
    # Allows the Streamlit frontend container to receive the food without cross-origin blocking
    output.headers.add("Access-Control-Allow-Origin", "*")
    
    return output  # Deliver the finished answer back to Streamlit!


# 5. COUNTER #2: THE KITCHEN CALL BELL / HEALTH CHECK (`/ping` route)
# A quick way for Streamlit to tap the counter and ask "Hey, is the kitchen online?"
@app.route("/ping", methods=["GET"])
def ping():
    # Instantly reply with "pong" (Yes, the restaurant is open and ready!)
    output = jsonify({"ack": "pong"})
    output.headers.add("Access-Control-Allow-Origin", "*")
    return output


# 6. UNLOCKING THE FRONT DOORS (Main Application Entrypoint)
# When you execute `python api.py`, this block fires up the server.
if __name__ == "__main__":
    # Check if a custom port was assigned in the environment (defaults to Port 5001)
    port = int(os.environ.get("PORT", 5001))
    
    # Run the restaurant!
    # '0.0.0.0' = Accept orders from any network address
    # 'port=port' = Listen specifically on Port 5001
    app.run(debug=True, host="0.0.0.0", port=port
