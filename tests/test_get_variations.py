import pytest
from amazon_paapi5.models.get_variations import GetVariationsRequest
from amazon_paapi5.resources import validate_resources

@pytest.mark.asyncio
async def test_get_variations_request():
    request = GetVariationsRequest(
        asin="B08L5V9T6R",
        variation_page=1,
        partner_tag="test_tag",
    )
    assert request.to_dict()["ASIN"] == "B08L5V9T6R"
    assert "VariationSummary.VariationDimension" in request.resources
    validate_resources("GetVariations", request.resources)