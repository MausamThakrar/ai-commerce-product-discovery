from app.models.conversation import ConversationContext
from app.search.commerce import CommerceSearchService
from app.search.conversation import ConversationService
from app.search.hybrid import HybridSearchEngine
from app.search.keyword import KeywordSearchEngine
from app.search.semantic import SemanticSearchEngine
from app.services.catalog import ProductCatalog


catalog = ProductCatalog()
products = catalog.all()

keyword_search = KeywordSearchEngine(products)
semantic_search = SemanticSearchEngine(products)

hybrid_search = HybridSearchEngine(
    products=products,
    keyword_search=keyword_search,
    semantic_search=semantic_search,
)

commerce_search = CommerceSearchService(
    products=products,
    hybrid_search=hybrid_search,
)

conversation = ConversationService(
    products=products,
    commerce_search=commerce_search,
)


def test_new_conversation_search():
    result = conversation.handle(
        "waterproof hiking shoes under €150",
        ConversationContext(),
    )

    assert result["action"] == "search"

    assert (
        result["context"].intent.category
        == "trail-shoes"
    )


def test_follow_up_color_refinement():
    initial = conversation.handle(
        "waterproof hiking shoes under €200",
        ConversationContext(),
    )

    refined = conversation.handle(
        "only black ones",
        initial["context"],
    )

    assert refined["action"] == "refine"

    assert (
        refined["context"].intent.color
        == "black"
    )

    for result in refined["results"]:
        assert (
            result["product"].attributes["color"]
            == "black"
        )


def test_cheapest_product_answer():
    initial = conversation.handle(
        "waterproof hiking shoes under €200",
        ConversationContext(),
    )

    answer = conversation.handle(
        "which is cheapest?",
        initial["context"],
    )

    assert answer["action"] == "answer"
    assert answer["selected_product"] is not None


def test_compare_first_two():
    initial = conversation.handle(
        "backpack for carrying things",
        ConversationContext(),
    )

    comparison = conversation.handle(
        "compare the first two",
        initial["context"],
    )

    assert comparison["action"] == "compare"
    assert len(comparison["comparison"]) == 2


def test_add_cheapest_to_cart():
    initial = conversation.handle(
        "waterproof hiking shoes under €200",
        ConversationContext(),
    )

    cart_action = conversation.handle(
        "add the cheapest one to cart",
        initial["context"],
    )

    assert cart_action["action"] == "add_to_cart"
    assert cart_action["selected_product"] is not None