from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import List, Dict, Any

class MenuOpenedEvent(BaseModel):
    pass

class MenuClosedEvent(BaseModel):
    pass

class MenuSystem(Concept):
    """
    Concept: MenuSystem
    Emits Events: MenuOpened, MenuClosed, ItemUsed, EquipItem
    """
    __events__ = {
        "MenuOpened": MenuOpenedEvent,
        "MenuClosed": MenuOpenedEvent, # Reusing simple pass
        "ItemUsed": BaseModel,
        "EquipItem": BaseModel
    }

    def __init__(self, name: str = "MenuSystem"):
        super().__init__(name)
        self.active = False
        self.state = "MAIN" # MAIN, ITEMS, EQUIP, STATUS, OPTIONS
        self.cursor = 0
        self.menu_items = ["Status", "Items", "Equipment", "Options", "Close"]
        
        # Local cache of player data for display
        self.player_stats = {
            "level": 1, "xp": 0, "next_xp": 100,
            "hp": 30, "max_hp": 30,
            "atk": 10, "def": 5, "spd": 5
        }
        self.inventory = []
        self.equipment = {}

    def open(self, payload: dict):
        """Action: open"""
        self.active = True
        self.state = "MAIN"
        self.cursor = 0
        self.emit("MenuOpened", {})
        print("Menu Opened")

    def close(self, payload: dict):
        """Action: close"""
        self.active = False
        self.emit("MenuClosed", {})
        print("Menu Closed")

    def update_player_data(self, payload: dict):
        """Action: update_player_data - Syncs stats/inventory from Player"""
        # Payload might contain partial updates, so update dict
        for k, v in payload.items():
            if k == "inventory":
                self.inventory = v
            elif k == "equipment":
                self.equipment = v
            else:
                self.player_stats[k] = v

    def handle_input(self, payload: dict):
        """Action: handle_input"""
        key = payload.get("key")
        
        if not self.active:
            if key == "MENU":
                self.open({})
            return

        if key == "UP":
            self.cursor = max(0, self.cursor - 1)
        elif key == "DOWN":
            max_c = len(self.menu_items) - 1
            if self.state == "ITEMS": max_c = max(0, len(self.inventory) - 1)
            # ... other states ...
            self.cursor = min(max_c, self.cursor + 1)
            
        elif key == "CONFIRM":
            self._handle_confirm()
        
        elif key == "CANCEL" or key == "MENU":
            if self.state == "MAIN":
                self.close({})
            else:
                self.state = "MAIN"
                self.cursor = 0

    def _handle_confirm(self):
        if self.state == "MAIN":
            selection = self.menu_items[self.cursor]
            if selection == "Close":
                self.close({})
            elif selection == "Status":
                self.state = "STATUS"
            elif selection == "Items":
                self.state = "ITEMS"
                self.cursor = 0
            elif selection == "Equipment":
                self.state = "EQUIP"
                self.cursor = 0
            elif selection == "Options":
                self.state = "OPTIONS"
                
        elif self.state == "ITEMS":
            if self.inventory:
                # Use Item
                pass
                
        elif self.state == "EQUIP":
            pass

    def draw(self, payload: dict):
        """Action: draw"""
        if not self.active: return
        import pyxel
        
        # Reset camera for UI
        pyxel.camera(0, 0)
        
        # Draw Window (Screen Center)
        x, y, w, h = 64, 32, 128, 128
        pyxel.rect(x, y, w, h, 0) # Black bg
        pyxel.rectb(x, y, w, h, 7) # White border
        
        if self.state == "MAIN":
            pyxel.text(x + 10, y + 10, "-- MENU --", 7)
            for i, item in enumerate(self.menu_items):
                col = 7
                if i == self.cursor: col = 8 # Highlight
                pyxel.text(x + 20, y + 30 + i * 10, item, col)
                
        elif self.state == "STATUS":
            s = self.player_stats
            pyxel.text(x + 10, y + 10, "-- STATUS --", 7)
            pyxel.text(x + 10, y + 30, f"Name: Hero", 7)
            pyxel.text(x + 10, y + 40, f"Level: {s.get('level')}", 7)
            pyxel.text(x + 10, y + 50, f"XP: {s.get('xp')} / {s.get('next_xp', 100)}", 7)
            pyxel.text(x + 10, y + 70, f"HP: {s.get('hp')} / {s.get('max_hp')}", 7)
            pyxel.text(x + 10, y + 80, f"ATK: {s.get('atk')}", 7)
            pyxel.text(x + 10, y + 90, f"DEF: {s.get('def')}", 7)
            pyxel.text(x + 10, y + 100, f"SPD: {s.get('spd')}", 7)
            
        elif self.state == "ITEMS":
            pyxel.text(x + 10, y + 10, "-- ITEMS --", 7)
            if not self.inventory:
                pyxel.text(x + 20, y + 30, "(Empty)", 6)
            else:
                # List items
                pass
