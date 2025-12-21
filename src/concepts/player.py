from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class MovedEvent(BaseModel):
    x: float
    y: float

class InteractedEvent(BaseModel):
    # TODO: Define fields for Interacted
    pass

class InteractionAttemptEvent(BaseModel):
    x: float
    y: float
    w: float
    h: float

class CheckCollisionEvent(BaseModel):
    x: float
    y: float
    
class MoveValidEvent(BaseModel):
    x: float
    y: float

class CheckEncounterEvent(BaseModel):
    x: float
    y: float

class Player(Concept):
    """
    Concept: Player
    Emits Events: Moved, InteractionAttempt, CheckCollision, CheckEncounter
    """
    __events__ = {
        "Moved": MovedEvent,
        "InteractionAttempt": InteractionAttemptEvent,
        "Interacted": InteractedEvent,
        "CheckCollision": CheckCollisionEvent,
        "CheckEncounter": CheckEncounterEvent
    }

    def __init__(self, name: str = "Player"):
        super().__init__(name)
        self.x = 120
        self.y = 120

    def initiate_move(self, payload: dict):
        """
        Action: initiate_move
        """
        dx = payload.get("dx", 0)
        dy = payload.get("dy", 0)
        
        # Calculate target based on speed
        target_x = self.x + dx * 2
        target_y = self.y + dy * 2
        
        # Emit check request
        self.emit("CheckCollision", {"x": target_x, "y": target_y})

    def confirm_move(self, payload: dict):
        """
        Action: confirm_move
        """
        self.x = payload.get("x", self.x)
        self.y = payload.get("y", self.y)
        self.emit("Moved", {"x": self.x, "y": self.y})
        # Trigger encounter check after successful move
        self.emit("CheckEncounter", {"x": self.x, "y": self.y})

    def interact(self, payload: dict):
        """
        Action: interact
        """
        # print("Player.interact called")
        # Emit an attempt event, passing player's position and size
        self.emit("InteractionAttempt", {
            "x": self.x,
            "y": self.y,
            "w": 16,
            "h": 16
        })
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

    def get_state_snapshot(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y
        }


