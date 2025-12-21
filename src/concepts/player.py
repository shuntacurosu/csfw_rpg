from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class MovedEvent(BaseModel):
    # TODO: Define fields for Moved
    pass

class InteractedEvent(BaseModel):
    # TODO: Define fields for Interacted
    pass

class Player(Concept):
    """
    Concept: Player
    Emits Events: Moved, Interacted
    """
    __events__ = {
        "Moved": MovedEvent,
        "Interacted": InteractedEvent
    }

    def __init__(self, name: str = "Player"):
        super().__init__(name)
        self.x = 120
        self.y = 120

    def move(self, payload: dict):
        """
        Action: move
        """
        dx = payload.get("dx", 0)
        dy = payload.get("dy", 0)
        self.x += dx * 2 # Speed 2
        self.y += dy * 2
        self.emit("Moved", {"x": self.x, "y": self.y})

    def interact(self, payload: dict):
        """
        Action: interact
        """
        # TODO: Implement interaction logic (check facing tile)
        pass

    def draw(self, payload: dict):
        """
        Action: draw
        """
        # print("Player.draw called")
        import pyxel
        # Draw player from sprite sheet
        # Hero is at (0, 16) in sprite sheet (row 2 col 1)
        pyxel.blt(self.x, self.y, 0, 0, 16, 16, 16, 0) # 0 is transparent color (black)


