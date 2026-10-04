import json
import random
from pathlib import Path


random.seed(42)


BRANDS = [
    "NordTrail",
    "PeakForge",
    "TerraRun",
    "AlpineCore",
    "WildPath",
]


PRODUCT_TYPES = {
    "trail-shoes": {
        "titles": [
            "Trail Runner",
            "Mountain Trek",
            "Alpine Grip",
            "Forest Runner",
            "Summit Trail",
        ],
        "uses": [
            "trail running",
            "hiking",
            "mountain trekking",
            "long-distance walking",
        ],
    },
    "hiking-jackets": {
        "titles": [
            "Storm Shell",
            "Alpine Jacket",
            "Mountain Shell",
            "Trail Jacket",
            "Weather Guard",
        ],
        "uses": [
            "hiking",
            "mountaineering",
            "winter trekking",
            "rainy weather",
        ],
    },
    "backpacks": {
        "titles": [
            "Trail Pack",
            "Summit Backpack",
            "Adventure Pack",
            "Trek Backpack",
            "Alpine Pack",
        ],
        "uses": [
            "day hiking",
            "travel",
            "mountain trekking",
            "weekend hiking",
        ],
    },
    "camping": {
        "titles": [
            "Explorer Tent",
            "Trail Shelter",
            "Mountain Tent",
            "Adventure Shelter",
            "Storm Camp",
        ],
        "uses": [
            "camping",
            "backpacking",
            "mountain camping",
            "weekend trips",
        ],
    },
}


COLORS = [
    "black",
    "blue",
    "green",
    "grey",
    "orange",
]


def create_product(index: int, category: str, config: dict) -> dict:
    brand = random.choice(BRANDS)

    product_type = random.choice(config["titles"])
    use_case = random.choice(config["uses"])

    waterproof = random.choice([True, True, False])
    lightweight = random.choice([True, False])

    color = random.choice(COLORS)

    price = round(random.uniform(49, 249), 2)

    title = f"{brand} {product_type} {index}"

    waterproof_text = (
        "waterproof and weather-resistant"
        if waterproof
        else "breathable and designed for dry conditions"
    )

    lightweight_text = (
        "lightweight"
        if lightweight
        else "durable and reinforced"
    )

    description = (
        f"A {lightweight_text} {product_type.lower()} designed for "
        f"{use_case}. It is {waterproof_text} and suitable for "
        f"outdoor adventures."
    )

    tags = [
        category,
        use_case,
        color,
    ]

    if waterproof:
        tags.append("waterproof")

    if lightweight:
        tags.append("lightweight")

    return {
        "id": f"product-{index}",
        "title": title,
        "description": description,
        "category": category,
        "brand": brand,
        "price": price,
        "currency": "EUR",
        "tags": tags,
        "attributes": {
            "waterproof": waterproof,
            "lightweight": lightweight,
            "color": color,
            "use_case": use_case,
        },
        "inventory": random.randint(0, 50),
        "variants": [
            {
                "id": f"variant-{index}-default",
                "sku": f"OUT-{index:04}",
                "title": "Default",
                "price": price,
                "available": True,
                "options": {},
            }
        ],
    }


def main():
    products = []

    index = 1

    for category, config in PRODUCT_TYPES.items():
        for _ in range(30):
            products.append(
                create_product(
                    index=index,
                    category=category,
                    config=config,
                )
            )

            index += 1

    output_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "products.json"
    )

    with output_path.open("w") as file:
        json.dump(products, file, indent=2)

    print(f"Generated {len(products)} products")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()