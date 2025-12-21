from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class MoveEvent(BaseModel):
    dx: int
    dy: int

class ActionEvent(BaseModel):
    # TODO: Define fields for Action
    pass

class CancelEvent(BaseModel):
    # TODO: Define fields for Cancel
    pass

class BattleCommandEvent(BaseModel):
    command_idx: int

class InputSystem(Concept):
    """
    Concept: InputSystem
    Emits Events: Move, Action, Cancel, BattleCommand
    """
    __events__ = {
        "Move": MoveEvent,
        "Action": ActionEvent,
        "Cancel": CancelEvent,
        "BattleCommand": BattleCommandEvent
    }

    def __init__(self, name: str = "InputSystem"):
        super().__init__(name)
        self.current_state = "EXPLORING"

    def update_state(self, payload: dict):
        """
        Action: update_state
        """
        self.current_state = payload.get("state", "EXPLORING")
        print(f"InputSystem state updated to {self.current_state}")

    def check_input(self, payload: dict):
        """
        Action: check_input
        """
        import pyxel
        
        if self.current_state == "EXPLORING":
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
                
        elif self.current_state == "BATTLE":
             if pyxel.btnp(pyxel.KEY_1):
                 self.emit("BattleCommand", {"command_idx": 1}) # Attack
             elif pyxel.btnp(pyxel.KEY_2):
                 self.emit("BattleCommand", {"command_idx": 2}) # Skill
             elif pyxel.btnp(pyxel.KEY_3):
                 self.emit("BattleCommand", {"command_idx": 3}) # Escape

