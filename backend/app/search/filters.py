from app.models.product import Product


def matches_filters(
    product: Product,
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    color: str | None = None,
    waterproof: bool | None = None,
    lightweight: bool | None = None,
    in_stock: bool | None = None,
) -> bool:

    if category is not None:
        if product.category.lower() != category.lower():
            return False

    if brand is not None:
        if product.brand.lower() != brand.lower():
            return False

    if min_price is not None and product.price < min_price:
        return False

    if max_price is not None and product.price > max_price:
        return False

    if color is not None:
        product_color = str(
            product.attributes.get("color", "")
        ).lower()

        if product_color != color.lower():
            return False

    if waterproof is not None:
        if product.attributes.get("waterproof") != waterproof:
            return False

    if lightweight is not None:
        if product.attributes.get("lightweight") != lightweight:
            return False

    if in_stock is not None:
        has_stock = product.inventory > 0

        if has_stock != in_stock:
            return False

    return True