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
    command: str

class MenuInputEvent(BaseModel):
    key: str

class InputSystem(Concept):
    """
    Concept: InputSystem
    Emits Events: Move, Action, Cancel, BattleCommand, MenuInput
    """
    __events__ = {
        "Move": MoveEvent,
        "Action": ActionEvent,
        "Cancel": CancelEvent,
        "BattleCommand": BattleCommandEvent,
        "MenuInput": MenuInputEvent
    }

    def __init__(self, name: str = "InputSystem"):
        super().__init__(name)
        self.current_state = "EXPLORING"

    def update_state(self, payload: dict):
        """
        Action: update_state
        """
        self.current_state = payload.get("state", "EXPLORING")
        print(f"InputSystem state: {self.current_state}")

    def check_input(self, payload: dict):
        """
        Action: check_input
        """
        import pyxel
        
        # Global Toggle (e.g. M key) - Allow opening menu from Exploring
        if self.current_state == "EXPLORING":
            if pyxel.btnp(pyxel.KEY_M):
                self.emit("MenuInput", {"key": "MENU"}) # Open Menu
                return

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
            
            if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_M):
                self.emit("Cancel", {})
                
        elif self.current_state == "BATTLE":
             if pyxel.btnp(pyxel.KEY_UP):
                 self.emit("BattleCommand", {"command": "Up"})
             elif pyxel.btnp(pyxel.KEY_DOWN):
                 self.emit("BattleCommand", {"command": "Down"})
             elif pyxel.btnp(pyxel.KEY_LEFT):
                 self.emit("BattleCommand", {"command": "Left"})
             elif pyxel.btnp(pyxel.KEY_RIGHT):
                 self.emit("BattleCommand", {"command": "Right"})
             elif pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
                 self.emit("BattleCommand", {"command": "Confirm"})
             elif pyxel.btnp(pyxel.KEY_X):
                 self.emit("BattleCommand", {"command": "Cancel"}) 

        elif self.current_state == "MENU" or self.current_state == "SHOP":
            if pyxel.btnp(pyxel.KEY_UP): 
                self.emit("MenuInput", {"key": "UP"})
            elif pyxel.btnp(pyxel.KEY_DOWN): 
                self.emit("MenuInput", {"key": "DOWN"})
            elif pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN): 
                self.emit("MenuInput", {"key": "CONFIRM"})
            elif pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_M): 
                self.emit("MenuInput", {"key": "CANCEL"})
            elif pyxel.btnp(pyxel.KEY_C):
                self.emit("MenuInput", {"key": "UNEQUIP"})

        elif self.current_state == "DIALOG":
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_SPACE):
                self.emit("Action", {}) # Close/Advance Dialog

