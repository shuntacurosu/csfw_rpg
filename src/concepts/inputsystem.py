from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class MoveEvent(BaseModel):
    # TODO: Define fields for Move
    pass

class ActionEvent(BaseModel):
    # TODO: Define fields for Action
    pass

class CancelEvent(BaseModel):
    # TODO: Define fields for Cancel
    pass

class InputSystem(Concept):
    """
    Concept: InputSystem
    Emits Events: Move, Action, Cancel
    """
    __events__ = {
        "Move": MoveEvent,
        "Action": ActionEvent,
        "Cancel": CancelEvent
    }

    def __init__(self, name: str = "InputSystem"):
        super().__init__(name)

    def check_input(self, payload: dict):
        """
        Action: check_input
        """
        import pyxel
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.emit("Move", {"dx": 0, "dy": -1})
        elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.emit("Move", {"dx": 0, "dy": 1})
        elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.emit("Move", {"dx": -1, "dy": 0})
        elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.emit("Move", {"dx": 1, "dy": 0})
        
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.emit("Action", {})
        
        if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.emit("Cancel", {})

