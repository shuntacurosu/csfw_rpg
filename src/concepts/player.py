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

class LevelUpEvent(BaseModel):
    level: int

class StatChangedEvent(BaseModel):
    hp: int
    max_hp: int
    atk: int
    def_stat: int = 0
    spd: int
    level: int
    xp: int
    next_xp: int

class Player(Concept):
    """
    Concept: Player
    Emits Events: Moved, InteractionAttempt, CheckCollision, CheckEncounter, LevelUp, StatChanged
    """
    __events__ = {
        "Moved": MovedEvent,
        "InteractionAttempt": InteractionAttemptEvent,
        "Interacted": InteractedEvent,
        "CheckCollision": CheckCollisionEvent,
        "CheckEncounter": CheckEncounterEvent,
        "LevelUp": LevelUpEvent,
        "StatChanged": StatChangedEvent
    }

    def load(self, payload: dict):
        """
        Action: load
        """
        print("Player loaded.")
        # Trigger initial stat calc and emit
        self.recalc_stats()

    def __init__(self, name: str = "Player"):
        super().__init__(name)
        self.x = 120 # Center of 16x16 map approx (7*16 + 8)
        self.y = 120
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        self.speed = 2
        
        # Stats
        self.name = "Hero"
        self.level = 1
        self.xp = 0
        self.next_level_xp = 100
        self.gold = 0
        
        # Base Stats
        self.base_max_hp = 30
        self.base_atk = 10
        self.base_def = 5
        self.base_spd = 5
        
        # Current Stats (Base + Equipment)
        self.max_hp = self.base_max_hp
        self.hp = self.max_hp
        self.atk = self.base_atk
        self.def_stat = self.base_def # 'def' is keyword
        self.spd = self.base_spd
        
        # Inventory & Equipment
        self.inventory = [] # List of Item Dicts
        self.equipment = {
            "weapon": None,
            "head": None,
            "body": None,
            "arms": None,
            "legs": None
        }

    def add_xp(self, payload: dict):
        """
        Action: add_xp
        """
        amount = payload.get("amount", 0)
        self.xp += amount
        print(f"Gained {amount} XP! Total: {self.xp}")
        self._check_level_up()

    def _check_level_up(self):
        # Simple XP Curve: Level * 100
        while self.xp >= self.next_level_xp and self.level < 30:
            self.xp -= self.next_level_xp
            self.level += 1
            self.next_level_xp = self.level * 100
            
            # Growth Table (Simple linear for now, can be complex table)
            self.base_max_hp += 5
            self.base_atk += 2
            self.base_def += 1
            self.base_spd += 1
            
            # Heal on Level Up
            self.hp = self.max_hp
            self.recalc_stats()
            
            print(f"LEVEL UP! Now Level {self.level}. Stats: HP{self.max_hp} ATK{self.atk} DEF{self.def_stat}")
            self.emit("LevelUp", {"level": self.level})

    def recalc_stats(self):
        # Reset to base
        self.max_hp = self.base_max_hp
        self.atk = self.base_atk
        self.def_stat = self.base_def
        self.spd = self.base_spd
        
        # Add Equipment stats
        for slot, item in self.equipment.items():
            if item:
                self.max_hp += item.get("hp_bonus", 0)
                self.atk += item.get("atk_bonus", 0)
                self.def_stat += item.get("def_bonus", 0)
                self.spd += item.get("spd_bonus", 0)
        
        # Clamp HP
        self.hp = min(self.hp, self.max_hp)
        self.emit("StatChanged", {
            "hp": self.hp, 
            "max_hp": self.max_hp, 
            "atk": self.atk, 
            "def": self.def_stat, 
            "spd": self.spd,
            "level": self.level,
            "xp": self.xp,
            "next_xp": self.next_level_xp
        })

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


