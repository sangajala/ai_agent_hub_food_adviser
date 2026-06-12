# Food Adviser AI Agent

A REST API that uses a LangGraph + Claude AI agent to search for restaurant and food options via Google Maps or TripAdvisor, powered by Apify scrapers.

## Requirements

- Python 3.9+
- An [Apify](https://apify.com) account and API token
- An [Anthropic](https://console.anthropic.com) API key

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/sangajala/ai_agent_hub_food_adviser.git
cd ai_agent_hub_food_adviser
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
APIFY_API_TOKEN=your_apify_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Running the Server

```bash
python app.py
```

The server starts on `http://localhost:5000` by default.

To use a different port:

```bash
PORT=8080 python app.py
```

> **Note:** macOS uses port 5000 for AirPlay. If you get a conflict, use `PORT=5001 python app.py`.

## API Endpoints

### `GET /health`

Check if the server is running.

```bash
curl http://localhost:5000/health
```

Response:
```json
{ "status": "ok" }
```

---

### `POST /search`

Search for food/restaurant options.

**Request body:**

| Field      | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| `location` | string | Yes      | City or area to search (e.g. `"New York City"`)  |
| `source`   | string | Yes      | Data source: `"google"` or `"tripadvisor"`       |
| `query`    | string | No       | Food type to search for (default: `"restaurants"`) |

**Example — Google Maps:**

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"location": "New York City", "source": "google", "query": "pizza"}'
```

**Example — TripAdvisor:**

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"location": "New York City", "source": "tripadvisor", "query": "pizza"}'
```

**Response:**

```json
{
  "location": "New York City",
  "query": "pizza",
  "source": "google",
  "results": [
    {
      "name": "Joe's Pizza",
      "rating": 4.8,
      "reviews_count": 3200,
      "address": "7 Carmine St, New York, NY",
      "url": "https://maps.google.com/...",
      "price_level": "$",
      "category": "Pizza"
    }
  ]
}
```

## Project Structure

```
ai_agent_hub_food_adviser/
├── app.py              # Flask entry point
├── agent/
│   ├── graph.py        # LangGraph agent (StateGraph)
│   ├── tools.py        # Apify tool definitions
│   └── state.py        # Agent state schema
├── requirements.txt
├── .env.example
└── .gitignore
```

## Agent Prompts

### 1. System Prompt (`agent/graph.py`)

Built dynamically per request based on the selected source:

```
You are a food adviser AI agent.
The user wants restaurant recommendations in '{location}' using {source_label}.
You MUST call ONLY the `{tool_name}` tool to fetch results — do not call the other tool.
After receiving the tool results, present the top options clearly with name, rating, address, and URL.
```

### 2. User Message (`app.py`)

Sent as the initial human message to the agent:

```
Find me food options for '{query}' in {location}.
```

### 3. Tool Descriptions (`agent/tools.py`)

Used by Claude to understand when to call each tool:

- **`search_google_maps`** — Search for restaurants and food options on Google Maps using Apify.
- **`search_tripadvisor`** — Search for restaurants and food options on TripAdvisor using Apify.

---

## How It Works

1. The `/search` endpoint receives a location, source, and query
2. A LangGraph agent is invoked with Claude as the LLM
3. Claude calls the appropriate Apify tool (`search_google_maps` or `search_tripadvisor`)
4. Apify scrapes the data source and returns restaurant results
5. The API returns the structured results as JSON
