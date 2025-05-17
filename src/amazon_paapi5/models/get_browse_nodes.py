from typing import List, Optional
from dataclasses import dataclass
from ..resources import validate_resources
from ..exceptions import InvalidParameterException

@dataclass
class GetBrowseNodesRequest:
    browse_node_ids: List[str]
    partner_tag: str = ""
    partner_type: str = "Associates"
    resources: List[str] = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = ["BrowseNodeInfo.BrowseNodes"]
        validate_resources("GetBrowseNodes", self.resources)
        if len(self.browse_node_ids) > 10:
            raise InvalidParameterException("GetBrowseNodes supports up to 10 browse node IDs per request.")
        if not self.browse_node_ids:
            raise InvalidParameterException("At least one browse_node_id is required.")

    def to_dict(self) -> dict:
        return {
            "BrowseNodeIds": self.browse_node_ids,
            "PartnerTag": self.partner_tag,
            "PartnerType": self.partner_type,
            "Resources": self.resources,
        }

@dataclass
class BrowseNode:
    id: str
    name: Optional[str] = None
    parent_id: Optional[str] = None

@dataclass
class GetBrowseNodesResponse:
    browse_nodes: List[BrowseNode]

    @classmethod
    def from_dict(cls, data: dict) -> 'GetBrowseNodesResponse':
        browse_nodes = [
            BrowseNode(
                id=node["Id"],
                name=node.get("DisplayName"),
                parent_id=node.get("Parent", {}).get("Id"),
            )
            for node in data.get("BrowseNodesResult", {}).get("BrowseNodes", [])
        ]
        return cls(browse_nodes=browse_nodes)