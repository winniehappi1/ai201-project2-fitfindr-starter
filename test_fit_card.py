from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe

results = search_listings("vintage graphic tee", max_price=30)
new_item = results[0]
wardrobe = get_example_wardrobe()

outfit = suggest_outfit(new_item, wardrobe)
fit_card = create_fit_card(outfit, new_item)

print(fit_card)