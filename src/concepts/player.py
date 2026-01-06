from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict, List


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
    gold: int = 0
    inventory: List[Dict[str, Any]] = []
    equipment: Dict[str, Any] = {}

class EquipItemEvent(BaseModel):
    slot: str
    item: dict

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
        "StatChanged": StatChangedEvent,
        "EquipItem": EquipItemEvent
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
        self.direction = "down"  # "down", "up", "left", "right"
        
        # Stats
        self.name = "Hero"
        self.level = 1
        self.xp = 0
        self.next_level_xp = 100
        self.gold = 10000  # Starting gold
        
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
            "shield": None, # Added
            "head": None,
            "body": None,
            "arms": None,
            "legs": None,
            "accessory": None # Added
        }

    def add_xp(self, payload: dict):
        """
        Action: add_xp
        """
        amount = payload.get("amount", 0)
        self.xp += amount
        print(f"Gained {amount} XP! Total: {self.xp}")
        self._check_level_up()
        # Ensure stats/XP updated in Menu even if no level up
        self.recalc_stats()

    def _check_level_up(self):
        # ... (keep existing _check_level_up)
        # Leveling Growth Table (Lv 1-30)
        # Stats: [MAX_HP, ATK, DEF, SPD]
        GROWTH_TABLE = {
            1: [30, 10, 5, 5],
            2: [35, 12, 6, 6],
            3: [42, 15, 8, 7],
            4: [50, 18, 10, 8],
            5: [60, 22, 12, 10],
            6: [72, 26, 15, 12],
            7: [85, 30, 18, 14],
            8: [100, 35, 22, 16],
            9: [120, 42, 26, 18],
            10: [150, 50, 30, 20],
            # ... can be expanded to 30 ...
            30: [1000, 250, 150, 100]
        }
        
        # Linear approximation for missing table values to avoid bloat
        def get_stat_growth(lv, idx):
            if lv in GROWTH_TABLE: return GROWTH_TABLE[lv][idx]
            # Interpolate
            prev_lv = max([k for k in GROWTH_TABLE.keys() if k < lv])
            next_lv = min([k for k in GROWTH_TABLE.keys() if k > lv])
            p_val = GROWTH_TABLE[prev_lv][idx]
            n_val = GROWTH_TABLE[next_lv][idx]
            return p_val + (n_val - p_val) * (lv - prev_lv) // (next_lv - prev_lv)

        while self.xp >= self.next_level_xp and self.level < 30:
            self.xp = 0 # Reset XP to 0 as requested
            self.level += 1
            self.next_level_xp = self.level * 100
            
            # Apply growth from table
            self.base_max_hp = int(get_stat_growth(self.level, 0))
            self.base_atk = int(get_stat_growth(self.level, 1))
            self.base_def = int(get_stat_growth(self.level, 2))
            self.base_spd = int(get_stat_growth(self.level, 3))
            
            # Heal on Level Up
            self.hp = self.base_max_hp
            self.recalc_stats()
            
            print(f"LEVEL UP! Hero reached Level {self.level}!")
            self.emit("LevelUp", {"level": self.level})

    def equip_item(self, payload: dict):
        """Action: equip_item"""
        slot = payload.get("slot")
        item = payload.get("item")
        if slot in self.equipment:
            old_item = self.equipment.get(slot)
            self.equipment[slot] = item
            if item:
                print(f"Equipped {item['name']} to {slot}")
            else:
                if old_item:
                    print(f"Unequipped {old_item['name']} from {slot}")
                else:
                    print(f"Nothing to unequip from {slot}")
            self.recalc_stats()

    def add_to_inventory(self, payload: dict):
        """Action: add_to_inventory"""
        item = payload.get("item")
        if item:
            # Deduct gold if item has a price
            price = item.get("price", 0)
            if price > 0:
                self.gold -= price
                print(f"Spent {price}G. Remaining gold: {self.gold}")
            
            self.inventory.append(item)
            print(f"Player inventory: {[i['name'] for i in self.inventory]}")
            self.recalc_stats()

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
            "def_stat": self.def_stat, 
            "spd": self.spd,
            "level": self.level,
            "xp": self.xp,
            "next_xp": self.next_level_xp,
            "gold": self.gold,
            "inventory": self.inventory,
            "equipment": self.equipment
        })

    def initiate_move(self, payload: dict):
        """
        Action: initiate_move
        """
        dx = payload.get("dx", 0)
        dy = payload.get("dy", 0)
        
        # Update facing direction
        if dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
        
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
        """Action: interact"""
        self.emit("InteractionAttempt", {
            "x": self.x,
            "y": self.y,
            "w": 16,
            "h": 16
        })

    def draw(self, payload: dict):
        """
        Action: draw
        Uses 4-directional sprites based on self.direction.
        Sprite positions: Down(0,16), Up(16,16), Left(32,16), Right(48,16)
        """
        import pyxel
        
        # Sprite U position based on direction
        direction_sprites = {
            "down": 0,
            "up": 16,
            "left": 32,
            "right": 48
        }
        sprite_u = direction_sprites.get(self.direction, 0)
        
        # Draw player with transparency (color 0)
        pyxel.blt(self.x, self.y, 0, sprite_u, 16, 16, 16, 0)

    def get_state_snapshot(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y
        }


