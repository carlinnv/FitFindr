# FitFindr

An AI-powered thrift shopping assistant that searches secondhand listings, suggests outfits from your wardrobe, and generates a shareable fit card — all from a single natural language query.

Built with a Groq LLM backend (Llama 3.3 70B) and a Gradio frontend.

---

## What's Included

```
FitFindr/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── tools.py                   # Three agent tools: search, outfit, fit card
├── agent.py                   # Planning loop and query parser
├── app.py                     # Gradio UI
├── planning.md                # Spec and agent diagram
└── requirements.txt
```

---

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

Run the app:
```bash
python app.py
```

---

## Tool Inventory

### `search_listings(description, size, max_price)`

Scores all listings by keyword overlap with `description`, filters by `size` and `max_price`, and returns results sorted best-match first.

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | `str` | Keywords describing the item (e.g. `"oversized blazer"`) |
| `size` | `str \| None` | Size code to filter by; case-insensitive, partial match (e.g. `"M"` matches `"S/M"`) |
| `max_price` | `float \| None` | Maximum price inclusive; `None` skips price filtering |

**Returns:** `list[dict]` — matching listings sorted by relevance score, or `[]` if nothing matches. Each dict has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`.

---

### `suggest_outfit(new_item, wardrobe)`

Calls the LLM to suggest 1–2 outfit combinations using the new item and pieces from the user's wardrobe.

| Parameter | Type | Description |
|-----------|------|-------------|
| `new_item` | `dict` | A listing dict for the item being considered |
| `wardrobe` | `dict` | A wardrobe dict with an `items` key containing a list of wardrobe item dicts |

**Returns:** `str` — 2–3 sentences naming specific wardrobe pieces and how to style the combination. If the wardrobe is empty, returns general styling advice for the item instead.

---

### `create_fit_card(outfit, new_item)`

Calls the LLM to generate a casual, shareable OOTD caption at `temperature=0.9` so output varies across runs.

| Parameter | Type | Description |
|-----------|------|-------------|
| `outfit` | `str` | The outfit suggestion string from `suggest_outfit()` |
| `new_item` | `dict` | The listing dict for the thrifted item to highlight |

**Returns:** `str` — a 2–4 sentence Instagram/TikTok caption mentioning the item name, price, and platform, ending with 3–5 hashtags. Returns a descriptive error string (does not raise) if `outfit` is empty or whitespace.

---

## Interaction Walkthrough

**User query:** `"I need a size medium oversized blazer under $50"`

**Step 1 — `search_listings`**
- **Input:** `description="I need a oversized blazer"`, `size="M"`, `max_price=50.0`
- **Why:** The agent parses the natural language query with regex to extract size (`medium` → normalized to `M`) and price (`under $50` → `50.0`), then searches for matching listings.
- **Output:** `[{"title": "Vintage Linen Blazer — Cream", "price": 38.0, "platform": "thredUp", "condition": "excellent", "size": "M/L", ...}, ...]` — top match stored in `session["selected_item"]`

**Step 2 — `suggest_outfit`**
- **Input:** `new_item=session["selected_item"]`, `wardrobe=get_example_wardrobe()`
- **Why:** With a listing confirmed, the agent passes it along with the user's wardrobe to the LLM to get specific pairing suggestions.
- **Output:** `"You can pair the Vintage Linen Blazer with the white ribbed tank top and wide-leg khaki trousers for a chic, summer-inspired look. Alternatively, combine the blazer with the baggy straight-leg jeans and black combat boots for a more edgy, contrasted outfit."` — stored in `session["outfit_suggestion"]`

**Step 3 — `create_fit_card`**
- **Input:** `outfit=session["outfit_suggestion"]`, `new_item=session["selected_item"]`
- **Why:** The agent passes the outfit string and item details to the LLM to produce a caption ready for social media.
- **Output:** `"Found this cream linen blazer on thredUp for $38 and it's the easiest piece I own — ribbed tank, wide-leg trousers, done. #ThriftedFit #LinenSzn #OOTD"`

**Final output to user:**
The Gradio UI populates three panels: the formatted listing (title, price, platform, condition, size, colors), the outfit suggestion, and the fit card caption.

---

## Error Handling and Fail Points

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No listings match the description, size, or price filter | Returns `[]`; the agent sets `session["error"]` with the failed filters and suggests broader terms, alternative names, or relaxed filters. Loop exits; `suggest_outfit` is never called. |
| `suggest_outfit` | Wardrobe is empty | The agent detects `wardrobe["items"] == []` before calling the tool and sets `session["error"]` asking the user to add wardrobe items. Loop exits; `create_fit_card` is never called. |
| `create_fit_card` | `outfit` string is empty or whitespace | Returns a descriptive error string (no exception). The agent also guards against this before calling the tool by checking `session["outfit_suggestion"]`. |

---

## Spec Reflection

**One way planning.md helped during implementation:**

The State Management section made the session dict design obvious before writing a single line of `run_agent`. Having `selected_item`, `wardrobe`, and `outfit` named and described in advance meant the loop almost wrote itself — each step just read the key it needed and wrote the key the next step expected. Without that, it would have been easy to pass values directly between calls and skip the session entirely, which would have made the early-exit error paths much harder to implement cleanly.

**One divergence from the spec, and why:**

The original spec described `search_listings` as returning an error message string when no results are found. During implementation, this was changed so the tool returns `[]` and the agent builds the error message instead. The tool is cleaner as a pure data function — it shouldn't know how to talk to users — and moving the message to the agent meant it could include the specific filters that were active (size, price), making the feedback more actionable. The test suite was updated to match.

---

## Demo

[![Watch the FitFindr demo](https://cdn.loom.com/sessions/thumbnails/e6a0f8859ebd4159b1ba159754bf55ea-with-play.gif)](https://www.loom.com/share/e6a0f8859ebd4159b1ba159754bf55ea)
