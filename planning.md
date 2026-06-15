# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

### Tool 1: search_listings

**What it does:**
Searches the mock listings dataset for secondhand clothing items that match the user's requested description, size, and maximum price.

**Input parameters:**
- `description` (str): The item or style the user wants, such as `"vintage graphic tee"`.
- `size` (str): The requested size, such as `"M"` or `"S/M"`. If the user does not give a size, this can be `None`.
- `max_price` (float): The highest price the user wants to pay.

**What it returns:**
A list of matching listing dictionaries. Each listing contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

**What happens if it fails or returns nothing:**
If no listings match, the agent tells the user no items were found and suggests broadening the description, increasing the budget, or removing the size filter. The agent does not continue to `suggest_outfit`.

---

### Tool 2: suggest_outfit

**What it does:**
Creates an outfit suggestion using the selected listing and the user's wardrobe. It matches the new item with wardrobe pieces based on category, color, and style tags.

**Input parameters:**
- `new_item` (dict): The selected listing from `search_listings`.
- `wardrobe` (dict): A wardrobe dictionary with an `items` list. Each item includes `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`.

**What it returns:**
An outfit suggestion that names the wardrobe pieces to wear with the new item and explains the style/vibe of the outfit.

**What happens if it fails or returns nothing:**
If the wardrobe is empty, the tool gives a general styling suggestion instead of crashing. It also tells the user that adding wardrobe items would make the recommendation more personalized.

---

### Tool 3: create_fit_card

**What it does:**
Turns the outfit suggestion into a short, shareable fit card that sounds like a social media caption.

**Input parameters:**
- `outfit` (str): The outfit suggestion returned by `suggest_outfit`.
- `new_item` (dict): The selected listing used in the outfit.

**What it returns:**
A short caption-style fit card that mentions the selected item, price/platform when useful, and the overall outfit vibe.

**What happens if it fails or returns nothing:**
If the outfit or item data is incomplete, the tool returns a clear message asking for the missing information instead of inventing details.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**

The agent first reads the user's request and extracts the item description, size if provided, maximum price if provided, and any style preferences or wardrobe details. It starts by calling `search_listings(description, size, max_price)` because the agent needs to find a real listing before it can suggest an outfit.

After `search_listings` runs, the agent checks the results. If the result list is empty, the agent stops early and tells the user that no matching listings were found. It suggests trying a broader description, increasing the budget, or removing the size filter. The agent does not call `suggest_outfit` or `create_fit_card` without a selected item.

If listings are found, the agent saves the first result as `selected_item` in the session state. Then it calls `suggest_outfit(selected_item, wardrobe)` using the selected listing and the user's wardrobe.

After `suggest_outfit` runs, the agent checks whether an outfit suggestion was created. If the wardrobe is empty, the agent still gives a general outfit suggestion and explains that adding more wardrobe items would make the result more personalized.

Finally, the agent calls `create_fit_card(outfit_suggestion, selected_item)` to create a short shareable caption. The agent is done when it can return three things to the user: the selected listing, the outfit suggestion, and the fit card.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

## Architecture

```text
User input
   |
   v
Planning Loop
   |
   |-- Extract:
   |      description
   |      size
   |      max_price
   |      wardrobe/style preferences
   |
   v
search_listings(description, size, max_price)
   |
   |-- If results == []
   |      |
   |      v
   |   Error response to user:
   |   "I couldn't find matching listings.
   |   Try a broader description, higher budget,
   |   or removing the size filter."
   |
   |-- If results found
          |
          v
   Session State:
   selected_item = results[0]
          |
          v
suggest_outfit(selected_item, wardrobe)
          |
          |-- If wardrobe is empty
          |      |
          |      v
          |   Return general styling suggestion
          |   and tell user more wardrobe items
          |   would improve the result.
          |
          |-- If wardrobe has items
                 |
                 v
          Session State:
          outfit_suggestion = returned outfit
                 |
                 v
create_fit_card(outfit_suggestion, selected_item)
                 |
                 |-- If outfit or item data is missing
                 |      |
                 |      v
                 |   Return clear missing-data message
                 |
                 |-- If successful
                        |
                        v
                 Session State:
                 fit_card = returned caption
                        |
                        v
Final response to user:
- Top matching listing
- Suggested outfit
- Shareable fit card
``` 

---

## AI Tool Plan

### Milestone 3 — Individual tool implementations

For Milestone 3, I will use ChatGPT to help implement each tool separately.

#### Tool 1: search_listings

I will provide ChatGPT with:
- The Tool 1 specification from this planning document
- The structure of `listings.json`
- The `load_listings()` function from `data_loader.py`

I expect ChatGPT to generate a Python function that:
- Loads the listings dataset
- Filters items by description
- Filters by size when provided
- Filters by maximum price when provided
- Returns matching listings

To verify the implementation, I will test:
1. A successful query such as `"vintage graphic tee"` under `$30`
2. A query with a specific size requirement
3. A query that should return no results

The tool passes verification if the returned listings match the dataset and the failure case returns an empty list.

#### Tool 2: suggest_outfit

I will provide ChatGPT with:
- The Tool 2 specification
- The wardrobe schema
- The example wardrobe from `wardrobe_schema.json`

I expect ChatGPT to generate a Python function that:
- Accepts a selected listing and wardrobe
- Finds wardrobe items with compatible styles, colors, or categories
- Generates a styling recommendation

To verify the implementation, I will:
1. Test with the example wardrobe
2. Confirm that matching pieces are recommended
3. Test with the empty wardrobe

The tool passes verification if it produces reasonable outfit suggestions and handles an empty wardrobe without crashing.

#### Tool 3: create_fit_card

I will provide ChatGPT with:
- The Tool 3 specification
- Examples of the desired caption style

I expect ChatGPT to generate a Python function that:
- Creates a short social-media-style caption
- References the selected item and outfit
- Produces concise and natural-sounding text

To verify the implementation, I will:
1. Test several outfit suggestions
2. Check that the caption includes relevant outfit information
3. Ensure no information is invented

The tool passes verification if the caption is readable, accurate, and consistent with the selected listing.

---

### Milestone 4 — Planning loop and state management

For Milestone 4, I will use ChatGPT to help implement the planning loop after all tools work individually.

I will provide:
- The Planning Loop section
- The Architecture diagram
- The Tool specifications
- The completed tool implementations

I expect ChatGPT to generate code that:
1. Reads the user's request
2. Calls `search_listings`
3. Checks whether results exist
4. Stores the selected listing in session state
5. Calls `suggest_outfit`
6. Stores the outfit suggestion in session state
7. Calls `create_fit_card`
8. Returns the final response to the user

To verify the implementation, I will test:

**Successful path**
- User requests a vintage graphic tee under $30
- Agent returns a listing, outfit suggestion, and fit card

**Failure path**
- User requests an item that does not exist
- Agent stops after `search_listings`
- Agent returns a helpful message instead of continuing

The planning loop passes verification if it calls tools in the correct order, handles errors correctly, and maintains state between tool calls.

---

## A Complete Interaction (Step by Step)

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

### Step 1:
The agent calls:

search_listings(
    description="vintage graphic tee",
    size=None,
    max_price=30.0
)

The tool searches the listings dataset and returns matching items.

Top result:

{
    "id": "lst_033",
    "title": "Vintage Band Tee — Faded Grey",
    "price": 19.00,
    "platform": "depop"
}

### Step 2:
The agent uses the selected item together with the user's wardrobe and calls:

suggest_outfit(
    new_item=<Vintage Band Tee>,
    wardrobe=<example_wardrobe>
)

The tool identifies pieces that match the vintage streetwear style and returns:

"Pair the Vintage Band Tee with the baggy straight-leg jeans and chunky white sneakers. Add the black crossbody bag for an everyday vintage streetwear outfit."

### Step 3:
The agent calls:

create_fit_card(
    outfit=<outfit suggestion>,
    new_item=<Vintage Band Tee>
)

The tool generates a short social-media style description:

"Found this faded vintage band tee for $19 and it goes perfectly with my baggy denim and chunky sneakers 🖤 Easy vintage streetwear fit."

### Final output to user:

Top Match:
- Vintage Band Tee — Faded Grey ($19 on Depop)

Suggested Outfit:
- Baggy straight-leg jeans
- Chunky white sneakers
- Black crossbody bag

Fit Card:
"Found this faded vintage band tee for $19 and it goes perfectly with my baggy denim and chunky sneakers 🖤 Easy vintage streetwear fit."

### Error Path

If search_listings returns no results, the agent informs the user that no matching items were found and suggests broadening the search criteria, increasing the budget, or removing size restrictions. The agent does not call suggest_outfit or create_fit_card with empty data.

## Data Loader Notes

The `utils/data_loader.py` file provides helper functions so the tools can access the mock data without manually opening JSON files each time.

`load_listings()` loads all items from `data/listings.json` and returns a list of listing dictionaries. Each listing includes fields like `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

`load_wardrobe_schema()` loads the full wardrobe schema from `data/wardrobe_schema.json`, including the schema, the example wardrobe, and the empty wardrobe.

`get_example_wardrobe()` returns the sample wardrobe with 10 items. This is useful for testing normal outfit suggestions.

`get_empty_wardrobe()` returns a wardrobe with an empty `items` list. This is useful for testing error handling when the user has not entered any wardrobe pieces yet.