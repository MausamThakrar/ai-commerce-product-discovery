from app.search.intent import parse_shopping_intent


def test_extracts_structured_shopping_intent():
    intent = parse_shopping_intent(
        "black waterproof hiking shoes under €120"
    )

    assert intent.category == "trail-shoes"
    assert intent.color == "black"
    assert intent.waterproof is True
    assert intent.max_price == 120
    assert intent.needs_clarification is False


def test_ambiguous_query_requires_clarification():
    intent = parse_shopping_intent(
        "something light for walking through wet mountains"
    )

    assert intent.category is None
    assert intent.lightweight is True
    assert intent.waterproof is True
    assert intent.needs_clarification is True
    assert intent.clarification_question is not None


def test_backpack_intent_from_natural_language():
    intent = parse_shopping_intent(
        "comfortable gear for carrying things "
        "on a weekend mountain trip"
    )

    assert intent.category == "backpacks"
    assert intent.needs_clarification is False


def test_price_range():
    intent = parse_shopping_intent(
        "hiking shoes between €80 and €140"
    )

    assert intent.min_price == 80
    assert intent.max_price == 140