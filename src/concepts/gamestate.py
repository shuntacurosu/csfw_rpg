from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class StateChangedEvent(BaseModel):
    state: str

class GameState(Concept):
    """
    Concept: GameState
    Emits Events: StateChanged
    """
    __events__ = {
        "StateChanged": StateChangedEvent
    }

    def __init__(self, name: str = "GameState"):
        super().__init__(name)
        self.current_state = "EXPLORING"

    def change_state(self, payload: dict):
        """
        Action: change_state
        """
        new_state = payload.get("state")
        if new_state and new_state != self.current_state:
            self.current_state = new_state
            self.emit("StateChanged", {"state": new_state})
