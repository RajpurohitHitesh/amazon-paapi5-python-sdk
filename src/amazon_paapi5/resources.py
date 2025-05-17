VALID_RESOURCES = {
    'SearchItems': [
        'ItemInfo.Title',
        'Offers.Listings.Price',
        'Images.Primary.Medium',
        'ItemInfo.ProductInfo',
        'ItemInfo.Classifications',
    ],
    'GetItems': [
        'ItemInfo.Title',
        'Offers.Listings.Price',
        'Images.Primary.Medium',
        'ItemInfo.ProductInfo',
        'ItemInfo.Classifications',
    ],
    'GetVariations': [
        'VariationSummary.VariationDimension',
        'ItemInfo.Title',
        'Offers.Listings.Price',
        'Images.Primary.Medium',
    ],
    'GetBrowseNodes': [
        'BrowseNodeInfo.BrowseNodes',
        'BrowseNodeInfo.WebsiteSalesRank',
    ],
}

def validate_resources(operation: str, resources: list) -> None:
    """Validate resources for the given operation."""
    valid = VALID_RESOURCES.get(operation, [])
    invalid = [r for r in resources if r not in valid]
    if invalid:
        raise ValueError(f"Invalid resources for {operation}: {invalid}")