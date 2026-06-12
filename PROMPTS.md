# Agent Prompts

This document lists all prompts used by the Food Adviser AI agent.

---

## 1. System Prompt

**File:** `agent/graph.py`

Built dynamically per request based on the user-selected data source:

```
You are a food adviser AI agent.
The user wants restaurant recommendations in '{location}' using {source_label}.
You MUST call ONLY the `{tool_name}` tool to fetch results — do not call the other tool.
After receiving the tool results, present the top options clearly with name, rating, address, and URL.
```

**Variables:**

| Variable | Example |
|---|---|
| `{location}` | `New York City` |
| `{source_label}` | `Google Maps` or `TripAdvisor` |
| `{tool_name}` | `search_google_maps` or `search_tripadvisor` |

---

## 2. User Message

**File:** `app.py`

Sent as the initial human message that starts the agent loop:

```
Find me food options for '{query}' in {location}.
```

**Variables:**

| Variable | Example |
|---|---|
| `{query}` | `pizza`, `sushi`, `restaurants` |
| `{location}` | `New York City` |

---

## 3. Tool Descriptions

**File:** `agent/tools.py`

These docstrings are passed to Claude so it understands when and how to call each tool.

### `search_google_maps`

```
Search for restaurants and food options on Google Maps using Apify.

Args:
    location: City or address to search in (e.g. 'New York City').
    query: Type of food or restaurant to search for (e.g. 'best pizza').

Returns:
    List of restaurant dicts with name, rating, address, url, reviews_count.
```

### `search_tripadvisor`

```
Search for restaurants and food options on TripAdvisor using Apify.

Args:
    location: City or area to search in (e.g. 'New York City').
    query: Type of food or restaurant to search for (e.g. 'best pizza').

Returns:
    List of restaurant dicts with name, rating, address, url, price_level.
```

---

## Prompt Flow

```
User Request
     │
     ▼
[System Prompt] + [User Message]
     │
     ▼
  Claude (LLM)
     │
     ▼
Tool Call: search_google_maps OR search_tripadvisor
     │
     ▼
Apify scrapes results
     │
     ▼
Claude receives tool output → Formats response
     │
     ▼
API returns structured JSON results
```
