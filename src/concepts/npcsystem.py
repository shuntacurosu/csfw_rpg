from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class DialogstartedEvent(BaseModel):
    # TODO: Define fields for DialogStarted
    pass

class NpcSystem(Concept):
    """
    Concept: NpcSystem
    Emits Events: DialogStarted
    """
    __events__ = {
        "DialogStarted": DialogstartedEvent
    }

    def __init__(self, name: str = "NpcSystem"):
        super().__init__(name)

    def load(self, payload: dict):
        """
        Action: load
        """
        # TODO: Implement logic
        # self.emit("SomeEvent", {})
        pass

    def update(self, payload: dict):
        """
        Action: update
        """
        # TODO: Implement logic
        # self.emit("SomeEvent", {})
        pass

    def draw(self, payload: dict):
        """
        Action: draw
        """
        # TODO: Implement npc rendering
        pass

