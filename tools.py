"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    listings = load_listings()

    query_words = set(description.lower().replace("-", " ").split())
    matches = []

    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue

        if size is not None:
            size_query = size.lower()
            item_size = item["size"].lower()
            if size_query not in item_size:
                continue

        searchable_text = " ".join([
            item.get("title", ""),
            item.get("description", ""),
            item.get("category", ""),
            " ".join(item.get("style_tags", [])),
            " ".join(item.get("colors", [])),
            item.get("brand") or "",
            item.get("platform", ""),
        ]).lower().replace("-", " ")

        title_text = item.get("title", "").lower().replace("-", " ")
        tag_text = " ".join(item.get("style_tags", [])).lower().replace("-", " ")
        description_text = item.get("description", "").lower().replace("-", " ")

        score = 0

        for word in query_words:
            if word in title_text:
                score += 4
            if word in tag_text:
                score += 3
            if word in description_text:
                score += 1

        # Bonus for exact phrases
        if "graphic tee" in tag_text or "graphic tee" in title_text:
            score += 5

        if "band tee" in tag_text or "band tee" in title_text:
            score += 4

        if score > 0:
            item_copy = item.copy()
            item_copy["_score"] = score
            matches.append(item_copy)

    matches.sort(key=lambda x: x["_score"], reverse=True)

    for item in matches:
        item.pop("_score", None)

    return matches


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = _get_groq_client()

    item_title = new_item.get("title", "this thrifted item")
    item_tags = ", ".join(new_item.get("style_tags", []))
    item_colors = ", ".join(new_item.get("colors", []))

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = f"""
You are FitFindr, a styling assistant.

The user is considering this thrifted item:
- Title: {item_title}
- Style tags: {item_tags}
- Colors: {item_colors}

The user's wardrobe is empty.

Give a helpful general outfit suggestion. Mention that adding wardrobe items would make the recommendation more personalized.
Keep it short and practical.
"""
    else:
        formatted_wardrobe = "\n".join(
            f"- {item['name']} ({item['category']}), colors: {', '.join(item['colors'])}, styles: {', '.join(item['style_tags'])}"
            for item in wardrobe_items
        )

        prompt = f"""
You are FitFindr, a styling assistant.

The user is considering this thrifted item:
- Title: {item_title}
- Style tags: {item_tags}
- Colors: {item_colors}

User wardrobe:
{formatted_wardrobe}

Suggest 1 complete outfit using the new item and specific named pieces from the wardrobe.
Keep it short, useful, and natural.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful fashion styling assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=250,
    )

    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "I need an outfit suggestion before I can create a fit card."

    client = _get_groq_client()

    item_title = new_item.get("title", "this thrifted item")
    price = new_item.get("price", "unknown price")
    platform = new_item.get("platform", "the thrift platform")

    prompt = f"""
Create a short social-media-style outfit caption.

Item:
- Title: {item_title}
- Price: ${price}
- Platform: {platform}

Outfit suggestion:
{outfit}

Requirements:
- 2 to 4 sentences
- Casual and authentic
- Mention the item name, price, and platform naturally
- Do not invent details
- Make it sound like an OOTD caption, not a product description
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You write casual outfit captions."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        max_tokens=180,
    )

    return response.choices[0].message.content.strip()