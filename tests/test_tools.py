from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

# ── shared fixtures ────────────────────────────────────────────────────────────

SAMPLE_ITEM = {
    "title": "Vintage Linen Blazer — Cream",
    "category": "outerwear",
    "colors": ["cream", "beige"],
    "condition": "excellent",
    "price": 38.0,
    "platform": "poshmark",
}

# ── search_listings ────────────────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_no_results_returns_empty_list():
    # search_listings is a pure data function — returns [] on no match
    result = search_listings("designer ballgown", size="XXS", max_price=5)
    assert result == []

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=50)
    assert isinstance(results, list)
    assert all(item["price"] <= 50 for item in results)

# ── suggest_outfit ─────────────────────────────────────────────────────────────

def test_suggest_outfit_populated_wardrobe_returns_string():
    result = suggest_outfit(SAMPLE_ITEM, get_example_wardrobe())
    assert isinstance(result, str)
    assert result.strip()

def test_suggest_outfit_empty_wardrobe_does_not_crash():
    # planning.md: empty wardrobe → return general styling advice, not an exception
    result = suggest_outfit(SAMPLE_ITEM, get_empty_wardrobe())
    assert isinstance(result, str)
    assert result.strip()

# ── create_fit_card ────────────────────────────────────────────────────────────

def test_create_fit_card_valid_returns_string():
    outfit = "Cream linen blazer over a white ribbed tank, wide-leg khakis, chunky sneakers."
    result = create_fit_card(outfit, SAMPLE_ITEM)
    assert isinstance(result, str)
    assert result.strip()

def test_create_fit_card_empty_outfit_returns_error_string():
    # planning.md: missing outfit → error string, not an exception
    result = create_fit_card("", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert result.strip()

def test_create_fit_card_whitespace_outfit_returns_error_string():
    result = create_fit_card("   ", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert result.strip()