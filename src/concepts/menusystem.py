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
                self.cursor = 0
            elif selection == "Items":
                self.state = "ITEMS"
                self.cursor = 0
            elif selection == "Equipment":
                self.state = "EQUIPMENT"
                self.cursor = 0
                self.sub_cursor = 0
                self.sub_state = "SELECT_SLOT"
            else:
                self.state = selection.upper()
                self.cursor = 0
                self.sub_cursor = 0
                self.sub_state = "SELECT_SLOT"
                
        elif self.state == "ITEMS":
            # Use item? (Not implemented)
            pass
                
        elif self.state == "EQUIPMENT":
            if self.sub_state == "SELECT_SLOT":
                self.sub_state = "SELECT_ITEM"
                self.sub_cursor = 0
            else:
                # Actually equip
                items = self._get_eligible_items()
                if items:
                    item = items[self.sub_cursor]
                    slot = self.equip_slots[self.cursor]
                    print(f"Equipping {item['name']} to {slot}")
                    self.emit("EquipItem", {"slot": slot, "item": item})
                    self.sub_state = "SELECT_SLOT"
            
        elif self.state == "OPTIONS":
            if self.cursor == 0: # Quit Game
                import pyxel
                pyxel.quit()

    def draw(self, payload: dict):
        """Action: draw"""
        if not self.active: return
        import pyxel
        pyxel.camera(0, 0)
        
        # Window
        x, y, w, h = 40, 20, 176, 180
        pyxel.rect(x, y, w, h, 0)
        pyxel.rectb(x, y, w, h, 7)
        
        if self.state == "MAIN":
            pyxel.text(x + 10, y + 10, "-- MENU --", 7)
            for i, item in enumerate(self.menu_items):
                col = 10 if i == self.cursor else 7
                pyxel.text(x + 20, y + 30 + i * 15, item, col)
                
        elif self.state == "STATUS":
            s = self.player_stats
            pyxel.text(x + 10, y + 10, "-- STATUS --", 7)
            pyxel.text(x + 10, y + 30, f"Name: Hero", 7)
            pyxel.text(x + 10, y + 42, f"Level: {s.get('level')}", 10)
            pyxel.text(x + 10, y + 54, f"XP: {s.get('xp')} / {s.get('next_xp', 100)}", 13)
            
            pyxel.text(x + 10, y + 74, f"HP: {s.get('hp')} / {s.get('max_hp')}", 7)
            pyxel.text(x + 10, y + 86, f"ATK: {s.get('atk')}", 7)
            pyxel.text(x + 10, y + 98, f"DEF: {s.get('def_stat', s.get('def'))}", 7)
            pyxel.text(x + 10, y + 110, f"SPD: {s.get('spd')}", 7)
            
        elif self.state == "ITEMS":
            pyxel.text(x + 10, y + 10, "-- ITEMS --", 7)
            if not self.inventory:
                pyxel.text(x + 20, y + 30, "(Empty)", 6)
            else:
                for i, item in enumerate(self.inventory):
                    col = 10 if i == self.cursor else 7
                    pyxel.text(x + 20, y + 30 + i*10, item["name"], col)
                    
        elif self.state == "EQUIPMENT":
            pyxel.text(x + 10, y + 10, "-- EQUIPMENT --", 7)
            for i, slot in enumerate(self.equip_slots):
                col = 10 if (i == self.cursor and self.sub_state == "SELECT_SLOT") else 7
                item = self.equipment.get(slot)
                val = item["name"] if item else "---"
                pyxel.text(x + 10, y + 30 + i*15, f"{slot.capitalize()}:", 6)
                pyxel.text(x + 60, y + 30 + i*15, val, col)

            if self.sub_state == "SELECT_ITEM":
                # Draw small selector on right
                ix, iy = x + 100, y + 30
                pyxel.rect(ix - 5, iy - 5, 75, 100, 1)
                pyxel.rectb(ix - 5, iy - 5, 75, 100, 7)
                items = self._get_eligible_items()
                if not items:
                    pyxel.text(ix, iy, "None", 6)
                else:
                    for i, item in enumerate(items):
                        col = 10 if i == self.sub_cursor else 7
                        pyxel.text(ix, iy + i*12, item["name"], col)

        elif self.state == "OPTIONS":
            pyxel.text(x + 10, y + 10, "-- OPTIONS --", 7)
            col = 10 if self.cursor == 0 else 7
            pyxel.text(x + 20, y + 30, "QUIT GAME", col)
