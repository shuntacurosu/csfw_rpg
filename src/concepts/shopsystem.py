from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import List, Dict, Any

class ItemBoughtEvent(BaseModel):
    item: Dict[str, Any]

class ShopSystem(Concept):
    """
    Concept: ShopSystem
    Handles shop interactions and inventory additions.
    """
    __events__ = {
        "ItemBought": ItemBoughtEvent,
        "ShopClosed": BaseModel
    }

    def __init__(self, name: str = "ShopSystem"):
        super().__init__(name)
        self.active = False
        self.shop_inventory = [
            {"name": "Potion", "type": "ITEM", "hp_bonus": 20, "desc": "Restores 20 HP"},
            {"name": "Iron Sword", "type": "weapon", "atk_bonus": 8, "desc": "+8 Attack"},
            {"name": "Steel Blade", "type": "weapon", "atk_bonus": 15, "desc": "+15 Attack"},
            {"name": "Buckler", "type": "shield", "def_bonus": 3, "desc": "+3 Defense"},
            {"name": "Kite Shield", "type": "shield", "def_bonus": 7, "desc": "+7 Defense"},
            {"name": "Iron Helm", "type": "head", "def_bonus": 2, "desc": "+2 Defense"},
            {"name": "Leather Vest", "type": "body", "def_bonus": 4, "desc": "+4 Defense"},
            {"name": "Steel Plate", "type": "body", "def_bonus": 12, "desc": "+12 Defense"},
            {"name": "Gantlets", "type": "arms", "def_bonus": 2, "desc": "+2 Defense"},
            {"name": "Iron Boots", "type": "legs", "def_bonus": 3, "desc": "+3 Defense"}
        ]
        self.cursor = 0

    def open_shop(self, payload: dict):
        """Action: open_shop"""
        npc_id = payload.get("npc_id")
        if npc_id not in [3, 6]:
            return
            
        self.active = True
        self.cursor = 0
        print(f"Shop Opened for NPC {npc_id}")

    def handle_input(self, payload: dict):
        """Action: handle_input"""
        if not self.active: return
        key = payload.get("key")
        
        if key == "UP":
            self.cursor = (self.cursor - 1) % len(self.shop_inventory)
        elif key == "DOWN":
            self.cursor = (self.cursor + 1) % len(self.shop_inventory)
        elif key == "CONFIRM":
            item = self.shop_inventory[self.cursor].copy()
            print(f"Acquired: {item['name']}")
            self.emit("ItemBought", {"item": item})
        elif key == "CANCEL":
            self.active = False
            self.emit("ShopClosed", {})
            print("Shop Closed")

    def draw(self, payload: dict):
        """Action: draw"""
        if not self.active: return
        import pyxel
        if not self.active: return
        import pyxel
        pyxel.camera(0, 0)
        
        # Draw Shop Window
        x, y, w, h = 20, 20, 216, 216
        pyxel.rect(x, y, w, h, 0) # Black BG
        pyxel.rectb(x, y, w, h, 7) # White Border
        pyxel.rect(x, y, w, 15, 1) # Header
        pyxel.text(x + 80, y + 5, "--- VILLAGE B SHOP ---", 7)
        
        # List items
        list_x = x + 10
        list_y = y + 25
        for i, item in enumerate(self.shop_inventory):
            color = 10 if i == self.cursor else 7
            if i == self.cursor:
                pyxel.rect(list_x - 2, list_y + i*14 - 2, 120, 12, 1)
            
            prefix = "> " if i == self.cursor else "  "
            pyxel.text(list_x, list_y + i*14, f"{prefix}{item['name']}", color)
            pyxel.text(list_x + 90, list_y + i*14, "FREE", 11)

        # Item Details Pane
        detail_x = x + 130
        detail_y = y + 25
        pyxel.rectb(detail_x - 5, detail_y - 5, 85, 100, 7)
        
        curr_item = self.shop_inventory[self.cursor]
        pyxel.text(detail_x, detail_y, "[DETAILS]", 6)
        pyxel.text(detail_x, detail_y + 15, curr_item["name"], 10)
        pyxel.text(detail_x, detail_y + 27, f"Type: {curr_item['type']}", 7)
        pyxel.text(detail_x, detail_y + 45, curr_item.get("desc", ""), 13)
        
        # Instructions
        pyxel.text(x + 10, y + h - 15, "CONFIRM: ACQUIRE  CANCEL: EXIT", 6)
