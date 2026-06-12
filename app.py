import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, render_template
from langchain_core.messages import HumanMessage

from agent.graph import food_agent

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/search")
def search():
    body = request.get_json(silent=True) or {}

    location = body.get("location", "").strip()
    source = body.get("source", "").strip().lower()
    query = body.get("query", "restaurants").strip()

    if not location:
        return jsonify({"error": "location is required"}), 400
    if source not in ("google", "tripadvisor"):
        return jsonify({"error": "source must be 'google' or 'tripadvisor'"}), 400

    initial_state = {
        "messages": [HumanMessage(content=f"Find me food options for '{query}' in {location}.")],
        "location": location,
        "source": source,
        "query": query,
        "results": [],
    }

    final_state = food_agent.invoke(initial_state)

    return jsonify(
        {
            "source": source,
            "location": location,
            "query": query,
            "results": final_state.get("results", []),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
