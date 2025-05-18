import pytest
from amazon_paapi5.models.get_items import GetItemsRequest
from amazon_paapi5.resources import validate_resources

@pytest.mark.asyncio
async def test_get_items_request():
    request = GetItemsRequest(
        item_ids=["B08L5V9T6R", "B07XVMJF2L"],
        partner_tag="test_tag",
    )
    assert request.to_dict()["ItemIds"] == ["B08L5V9T6R", "B07XVMJF2L"]
    assert "ItemInfo.Title" in request.resources
    validate_resources("GetItems", request.resources)