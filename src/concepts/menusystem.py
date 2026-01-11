from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import List, Dict, Any

class MenuOpenedEvent(BaseModel):
    pass

class MenuClosedEvent(BaseModel):
    pass

class EquipItemEvent(BaseModel):
    slot: str
    item: Any = None  # Can be None for unequip

class MenuSystem(Concept):
    """
    Concept: MenuSystem
    Emits Events: MenuOpened, MenuClosed, ItemUsed, EquipItem
    """
    __events__ = {
        "MenuOpened": MenuOpenedEvent,
        "MenuClosed": MenuClosedEvent,
        "ItemUsed": BaseModel,
        "EquipItem": EquipItemEvent
    }

    def __init__(self, name: str = "MenuSystem"):
        super().__init__(name)
        self.active = False
        self.state = "MAIN" # MAIN, ITEMS, EQUIP, STATUS, OPTIONS
        self.cursor = 0
        self.menu_items = ["Status", "Items", "Equipment", "Map", "Options", "Close"]
        self.equip_slots = ["weapon", "shield", "head", "body", "arms", "legs", "accessory"]
        self.sub_state = "SELECT_SLOT"
        self.sub_cursor = 0
        
        # Local cache of player data for display
        self.player_stats = {
            "level": 1, "xp": 0, "next_xp": 100,
            "hp": 30, "max_hp": 30,
            "atk": 10, "def": 5, "spd": 5,
            "gold": 0
        }
        self.inventory = []
        self.equipment = {}
        
        # World Map Data
        self.world_map = None
        self.player_x = 0
        self.player_y = 0
        self._load_world_map()

    def _load_world_map(self):
        import json
        import os
        try:
            # Load from split JSON structure
            # Load from split JSON structure
            base_dir = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(base_dir, "assets", "data", "maps", "world_map.json") 
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.world_map = json.load(f)
            print(f"World Map Loaded: {self.world_map is not None}")
        except Exception as e:
            print(f"Failed to load world map: {e}")

    def update_position(self, payload: dict):
        """Action: update_position"""
        self.player_x = payload.get("x", 0)
        self.player_y = payload.get("y", 0)

    def _get_eligible_items(self):
        """Get items that can be equipped in the currently selected slot."""
        if self.cursor >= len(self.equip_slots):
            return []
        slot = self.equip_slots[self.cursor]
        # Find items in inventory that match this slot type
        return [i for i in self.inventory if i.get("type", "").lower() == slot.lower()]

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

        if self.state == "MAP":
            if key == "CANCEL" or key == "CONFIRM" or key == "MENU":
                self.state = "MAIN"
                self.cursor = 0
            return

        # Handle EQUIPMENT sub-state navigation separately
        if self.state == "EQUIPMENT" and self.sub_state == "SELECT_ITEM":
            items = self._get_eligible_items()
            if key == "UP":
                self.sub_cursor = max(0, self.sub_cursor - 1)
            elif key == "DOWN":
                self.sub_cursor = min(len(items) - 1, self.sub_cursor + 1) if items else 0
            elif key == "CONFIRM":
                self._handle_confirm()
            elif key == "CANCEL":
                self.sub_state = "SELECT_SLOT"
            return

        # Handle UNEQUIP in EQUIPMENT SELECT_SLOT state
        if self.state == "EQUIPMENT" and self.sub_state == "SELECT_SLOT":
            if key == "UNEQUIP":
                slot = self.equip_slots[self.cursor]
                if self.equipment.get(slot):
                    print(f"Unequipping {self.equipment[slot]['name']} from {slot}")
                    self.emit("EquipItem", {"slot": slot, "item": None})
                return

        if key == "UP":
            self.cursor = max(0, self.cursor - 1)
        elif key == "DOWN":
            max_c = len(self.menu_items) - 1
            if self.state == "ITEMS":
                consumables = [i for i in self.inventory if i.get("type", "").upper() == "ITEM"]
                max_c = max(0, len(consumables) - 1)
            elif self.state == "EQUIPMENT":
                max_c = len(self.equip_slots) - 1
            elif self.state == "STATUS":
                max_c = 0
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
            elif selection == "Map":
                self.state = "MAP"
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
                
        elif self.state == "MAP":
            pyxel.text(x + 10, y + 10, "-- WORLD MAP --", 7)
            
            # Map Area
            mx = x + 24
            my = y + 25
            pyxel.rectb(mx - 1, my - 1, 130, 130, 1)
            
            if self.world_map:
                # Support layer-based structure
                layers = self.world_map.get("layers", {})
                tiles = layers.get("ground", [])
                if not tiles:
                    # Fallback to old 'tiles' key just in case
                    tiles = self.world_map.get("tiles", [])
                cols = {0: 11, 1: 5, 2: 12, 3: 4, 4: 3, 5: 10, 6: 13, 7: 9, 8: 8, 9: 8, 64: 8, 65: 8, 66: 8, 67: 8}
                for ty, row in enumerate(tiles):
                    for tx, tile in enumerate(row):
                        col = cols.get(tile, 0)
                        if col != 0:
                            pyxel.rect(mx + tx*2, my + ty*2, 2, 2, col)
                
                # Draw Portals
                # Filter dungeon portals (Target Map 10, 11, 12)
                for p in self.world_map.get("portals", []):
                    if p.get("target_map") in [10, 11, 12]:
                        col = 10 if (pyxel.frame_count // 5) % 2 == 0 else 9
                        px = mx + p.get("x") * 2
                        py = my + p.get("y") * 2
                        pyxel.rectb(px - 1, py - 1, 4, 4, col)
                        
                # Draw Player
                plx = mx + int(self.player_x / 8)
                ply = my + int(self.player_y / 8)
                pyxel.rect(plx, ply, 2, 2, 8)

        elif self.state == "STATUS":
            s = self.player_stats
            pyxel.text(x + 10, y + 10, "-- STATUS --", 7)
            pyxel.text(x + 10, y + 30, f"Name: Hero", 7)
            pyxel.text(x + 10, y + 42, f"Level: {s.get('level')}", 10)
            pyxel.text(x + 10, y + 54, f"XP: {s.get('xp')} / {s.get('next_xp', 100)}", 13)
            pyxel.text(x + 10, y + 66, f"Gold: {s.get('gold', 0)}G", 11)
            
            pyxel.text(x + 10, y + 86, f"HP: {s.get('hp')} / {s.get('max_hp')}", 7)
            pyxel.text(x + 10, y + 98, f"ATK: {s.get('atk')}", 7)
            pyxel.text(x + 10, y + 110, f"DEF: {s.get('def_stat', s.get('def'))}", 7)
            pyxel.text(x + 10, y + 122, f"SPD: {s.get('spd')}", 7)
            
        elif self.state == "ITEMS":
            pyxel.text(x + 10, y + 10, "-- ITEMS --", 7)
            # Only show consumable items (type == ITEM)
            consumables = [i for i in self.inventory if i.get("type", "").upper() == "ITEM"]
            if not consumables:
                pyxel.text(x + 20, y + 30, "(Empty)", 6)
            else:
                for i, item in enumerate(consumables):
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

            # Navigation hints
            if self.sub_state == "SELECT_SLOT":
                pyxel.text(x + 10, y + h - 15, "[Z]: Select  [C]: Unequip  [X]: Back", 6)
            else:
                pyxel.text(x + 10, y + h - 15, "[Z]: Equip  [X]: Cancel", 6)

            if self.sub_state == "SELECT_ITEM":
                # Draw item selector on right
                ix, iy = x + 100, y + 25
                pyxel.rect(ix - 5, iy - 5, 75, 80, 1)
                pyxel.rectb(ix - 5, iy - 5, 75, 80, 7)
                items = self._get_eligible_items()
                if not items:
                    pyxel.text(ix, iy, "None", 6)
                else:
                    for i, item in enumerate(items):
                        col = 10 if i == self.sub_cursor else 7
                        pyxel.text(ix, iy + i*12, item["name"], col)
                
                # Show stat comparison
                if items and self.sub_cursor < len(items):
                    selected_item = items[self.sub_cursor]
                    s = self.player_stats
                    
                    # Calculate stat changes
                    # Calculate stat changes based on difference
                    item_bonus_atk = selected_item.get("atk_bonus", 0)
                    item_bonus_def = selected_item.get("def_bonus", 0)
                    
                    # Current equipped item bonus
                    slot = self.equip_slots[self.cursor]
                    current_item = self.equipment.get(slot)
                    current_bonus_atk = current_item.get("atk_bonus", 0) if current_item else 0
                    current_bonus_def = current_item.get("def_bonus", 0) if current_item else 0
                    
                    atk_change = item_bonus_atk - current_bonus_atk
                    def_change = item_bonus_def - current_bonus_def
                    
                    # Show comparison below equipment list
                    cmp_y = y + 125
                    pyxel.text(x + 10, cmp_y, "-- STAT PREVIEW --", 6)
                    
                    # ATK
                    curr_atk = s.get("atk", 0)
                    new_atk = curr_atk + atk_change
                    atk_col = 10 if atk_change > 0 else (8 if atk_change < 0 else 7)
                    atk_arrow = "+" if atk_change > 0 else ""
                    pyxel.text(x + 10, cmp_y + 12, f"ATK: {curr_atk} -> {new_atk} ({atk_arrow}{atk_change})", atk_col)
                    
                    # DEF
                    curr_def = s.get("def_stat", s.get("def", 0))
                    new_def = curr_def + def_change
                    def_col = 10 if def_change > 0 else (8 if def_change < 0 else 7)
                    def_arrow = "+" if def_change > 0 else ""
                    pyxel.text(x + 10, cmp_y + 24, f"DEF: {curr_def} -> {new_def} ({def_arrow}{def_change})", def_col)

        elif self.state == "OPTIONS":
            pyxel.text(x + 10, y + 10, "-- OPTIONS --", 7)
            col = 10 if self.cursor == 0 else 7
            pyxel.text(x + 20, y + 30, "QUIT GAME", col)
