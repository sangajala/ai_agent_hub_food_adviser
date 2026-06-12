import os
from apify_client import ApifyClient
from langchain_core.tools import tool


def _get_client() -> ApifyClient:
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN environment variable is not set")
    return ApifyClient(token)


@tool
def search_google_maps(location: str, query: str) -> list:
    """Search for restaurants and food options on Google Maps using Apify.

    Args:
        location: City or address to search in (e.g. 'New York City').
        query: Type of food or restaurant to search for (e.g. 'best pizza').

    Returns:
        List of restaurant dicts with name, rating, address, url, reviews_count.
    """
    client = _get_client()
    run = client.actor("compass/crawler-google-places").call(
        run_input={
            "searchStringsArray": [f"{query} in {location}"],
            "maxCrawledPlacesPerSearch": 10,
            "language": "en",
            "exportPlaceUrls": True,
        }
    )
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(
            {
                "name": item.get("title", ""),
                "rating": item.get("totalScore"),
                "reviews_count": item.get("reviewsCount"),
                "address": item.get("address", ""),
                "url": item.get("url", ""),
                "price_level": item.get("price", ""),
                "category": item.get("categoryName", ""),
            }
        )
    return items


@tool
def search_tripadvisor(location: str, query: str) -> list:
    """Search for restaurants and food options on TripAdvisor using Apify.

    Args:
        location: City or area to search in (e.g. 'New York City').
        query: Type of food or restaurant to search for (e.g. 'best pizza').

    Returns:
        List of restaurant dicts with name, rating, address, url, price_level.
    """
    client = _get_client()
    run = client.actor("maxcopell/tripadvisor").call(
        run_input={
            "locationFullName": location,
            "includeRestaurants": True,
            "includeHotels": False,
            "includeAttractions": False,
            "maxItemsPerQuery": 10,
            "query": query,
        }
    )
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(
            {
                "name": item.get("name", ""),
                "rating": item.get("rating"),
                "reviews_count": item.get("numberOfReviews"),
                "address": item.get("address", ""),
                "url": item.get("url", ""),
                "price_level": item.get("priceLevel", ""),
                "category": item.get("cuisines", ""),
            }
        )
    return items
