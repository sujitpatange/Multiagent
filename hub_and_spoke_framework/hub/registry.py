from typing import Dict, List, Optional
from common.models import SpokeCapability

class SpokeMetadata:
    def __init__(self, name: str, capabilities: List[SpokeCapability], endpoint: str):
        self.name = name
        self.capabilities = capabilities
        self.endpoint = endpoint
        self.status = "active"

class AgentRegistry:
    def __init__(self):
        self._spokes: Dict[str, SpokeMetadata] = {}

    def register_spoke(self, name: str, capabilities: List[SpokeCapability], endpoint: str):
        self._spokes[name] = SpokeMetadata(name, capabilities, endpoint)
        print(f"Registered Spoke: {name} with capabilities: {capabilities}")

    def get_spokes_for_capability(self, capability: SpokeCapability) -> List[SpokeMetadata]:
        return [
            spoke for spoke in self._spokes.values()
            if capability in spoke.capabilities and spoke.status == "active"
        ]

    def list_all_spokes(self) -> List[SpokeMetadata]:
        return list(self._spokes.values())

    def update_spoke_status(self, name: str, status: str):
        if name in self._spokes:
            self._spokes[name].status = status
