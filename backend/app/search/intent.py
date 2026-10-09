import re

from app.models.intent import ShoppingIntent


CATEGORY_TERMS = {
    "trail-shoes": [
        "trail shoes",
        "hiking shoes",
        "walking shoes",
        "shoe",
        "shoes",
        "footwear",
        "trail runner",
        "trail runners",
    ],
    "hiking-jackets": [
        "hiking jacket",
        "hiking jackets",
        "jacket",
        "jackets",
        "coat",
        "shell",
    ],
    "backpacks": [
        "backpack",
        "backpacks",
        "rucksack",
        "bag",
        "carrying things",
        "carry things",
        "carry gear",
    ],
    "camping": [
        "tent",
        "tents",
        "shelter",
        "camping shelter",
        "camping",
    ],
}


CATEGORY_LABELS = {
    "trail-shoes": "footwear",
    "hiking-jackets": "a jacket",
    "backpacks": "a backpack",
    "camping": "camping equipment",
}


COLORS = [
    "black",
    "blue",
    "green",
    "grey",
    "gray",
    "orange",
]


WATERPROOF_TERMS = [
    "waterproof",
    "rainproof",
    "rain proof",
    "weather resistant",
    "weather-resistant",
    "keep me dry",
    "stay dry",
    "wet weather",
    "rainy weather",
    "wet mountains",
]


LIGHTWEIGHT_TERMS = [
    "lightweight",
    "light weight",
    "not heavy",
]


def _extract_category(query: str):
    matches = []

    for category, terms in CATEGORY_TERMS.items():
        if any(term in query for term in terms):
            matches.append(category)

    return matches


def _extract_prices(query: str):
    min_price = None
    max_price = None

    between_match = re.search(
        r"(?:between|from)\s*€?\s*(\d+(?:\.\d+)?)"
        r"\s*(?:and|to|-)\s*€?\s*(\d+(?:\.\d+)?)",
        query,
    )

    if between_match:
        min_price = float(between_match.group(1))
        max_price = float(between_match.group(2))

        return min_price, max_price

    max_match = re.search(
        r"(?:under|below|less than|up to|max(?:imum)?(?: of)?)"
        r"\s*€?\s*(\d+(?:\.\d+)?)",
        query,
    )

    if max_match:
        max_price = float(max_match.group(1))

    min_match = re.search(
        r"(?:over|above|more than|at least|min(?:imum)?(?: of)?)"
        r"\s*€?\s*(\d+(?:\.\d+)?)",
        query,
    )

    if min_match:
        min_price = float(min_match.group(1))

    return min_price, max_price


def parse_shopping_intent(
    query: str,
    brands: list[str] | None = None,
    require_category: bool = True,
) -> ShoppingIntent:

    normalized = query.lower().strip()

    categories = _extract_category(normalized)

    min_price, max_price = _extract_prices(
        normalized
    )

    color = None

    for candidate in COLORS:
        if re.search(
            rf"\b{re.escape(candidate)}\b",
            normalized,
        ):
            color = (
                "grey"
                if candidate == "gray"
                else candidate
            )
            break

    waterproof = None

    if "not waterproof" in normalized:
        waterproof = False

    elif any(
        term in normalized
        for term in WATERPROOF_TERMS
    ):
        waterproof = True

    lightweight = None

    if (
        "not lightweight" in normalized
        or "heavy" in normalized
    ):
        lightweight = False

    elif any(
        term in normalized
        for term in LIGHTWEIGHT_TERMS
    ):
        lightweight = True

    elif re.search(r"\blight\b", normalized):
        lightweight = True

    in_stock = None

    if (
        "in stock" in normalized
        or "available now" in normalized
    ):
        in_stock = True

    brand = None

    if brands:
        for candidate in brands:
            if candidate.lower() in normalized:
                brand = candidate
                break

    intent = ShoppingIntent(
        category=(
            categories[0]
            if len(categories) == 1
            else None
        ),
        category_candidates=categories,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        color=color,
        waterproof=waterproof,
        lightweight=lightweight,
        in_stock=in_stock,
    )

    if len(categories) > 1:
        labels = [
            CATEGORY_LABELS[category]
            for category in categories
        ]

        intent.needs_clarification = True

        intent.clarification_question = (
            "I found multiple possible product types. "
            f"Are you looking for {', '.join(labels)}?"
        )

    elif len(categories) == 0 and require_category:
        intent.needs_clarification = True

        intent.clarification_question = (
            "What type of product are you looking for: "
            "footwear, a jacket, a backpack, "
            "or camping equipment?"
        )

    return intent