import pytest
from amazon_paapi5.models.get_browse_nodes import GetBrowseNodesRequest
from amazon_paapi5.resources import validate_resources

@pytest.mark.asyncio
async def test_get_browse_nodes_request():
    request = GetBrowseNodesRequest(
        browse_node_ids=["123456", "789012"],
        partner_tag="test_tag",
    )
    assert request.to_dict()["BrowseNodeIds"] == ["123456", "789012"]
    assert "BrowseNodeInfo.BrowseNodes" in request.resources
    validate_resources("GetBrowseNodes", request.resources)