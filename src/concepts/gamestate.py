from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class ChangedEvent(BaseModel):
    # TODO: Define fields for Changed
    pass

class GameState(Concept):
    """
    Concept: GameState
    Emits Events: Changed
    """
    __events__ = {
        "Changed": ChangedEvent
    }

    def __init__(self, name: str = "GameState"):
        super().__init__(name)

    def change_state(self, payload: dict):
        """
        Action: change_state
        """
        # TODO: Implement logic
        # self.emit("SomeEvent", {})
        pass

