from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import List, Dict, Any

class ItemBoughtEvent(BaseModel):
    item: Dict[str, Any]

class ShopClosedEvent(BaseModel):
    pass

class ShopSystem(Concept):
    """
    Concept: ShopSystem
    Handles shop interactions and inventory additions.
    """
    __events__ = {
        "ItemBought": ItemBoughtEvent,
        "ShopClosed": ShopClosedEvent
    }

    def __init__(self, name: str = "ShopSystem"):
        super().__init__(name)
        self.active = False
        self.confirming = False  # Confirmation dialog state
        self.player_gold = 0  # Synced from player
        self.shop_inventory = [
            {"name": "Potion", "type": "ITEM", "hp_bonus": 20, "price": 50, "desc": "Restores 20 HP"},
            {"name": "Iron Sword", "type": "weapon", "atk_bonus": 8, "price": 150, "desc": "+8 Attack"},
            {"name": "Steel Blade", "type": "weapon", "atk_bonus": 15, "price": 300, "desc": "+15 Attack"},
            {"name": "Buckler", "type": "shield", "def_bonus": 3, "price": 80, "desc": "+3 Defense"},
            {"name": "Kite Shield", "type": "shield", "def_bonus": 7, "price": 200, "desc": "+7 Defense"},
            {"name": "Iron Helm", "type": "head", "def_bonus": 2, "price": 60, "desc": "+2 Defense"},
            {"name": "Leather Vest", "type": "body", "def_bonus": 4, "price": 100, "desc": "+4 Defense"},
            {"name": "Steel Plate", "type": "body", "def_bonus": 12, "price": 400, "desc": "+12 Defense"},
            {"name": "Gantlets", "type": "arms", "def_bonus": 2, "price": 70, "desc": "+2 Defense"},
            {"name": "Iron Boots", "type": "legs", "def_bonus": 3, "price": 90, "desc": "+3 Defense"}
        ]
        self.cursor = 0

    def update_player_gold(self, payload: dict):
        """Action: update_player_gold - Syncs gold from Player"""
        self.player_gold = payload.get("gold", 0)

    def open_shop(self, payload: dict):
        """Action: open_shop"""
        npc_id = payload.get("npc_id")
        if npc_id not in [3, 6]:
            return
            
        self.active = True
        self.confirming = False
        self.cursor = 0
        print(f"Shop Opened for NPC {npc_id}")

    def handle_input(self, payload: dict):
        """Action: handle_input"""
        if not self.active: 
            return
        key = payload.get("key")
        
        if self.confirming:
            # Confirmation dialog active
            if key == "CONFIRM":
                item = self.shop_inventory[self.cursor].copy()
                print(f"Acquired: {item['name']}")
                self.emit("ItemBought", {"item": item})
                self.confirming = False
            elif key == "CANCEL":
                self.confirming = False
        else:
            # Normal shop navigation
            if key == "UP":
                self.cursor = (self.cursor - 1) % len(self.shop_inventory)
            elif key == "DOWN":
                self.cursor = (self.cursor + 1) % len(self.shop_inventory)
            elif key == "CONFIRM":
                self.confirming = True  # Show confirmation dialog
            elif key == "CANCEL":
                self.active = False
                self.emit("ShopClosed", {})
                print("Shop Closed")

    def draw(self, payload: dict):
        """Action: draw"""
        if not self.active: return
        import pyxel
        pyxel.camera(0, 0)
        
        # Draw Shop Window
        x, y, w, h = 20, 20, 216, 216
        pyxel.rect(x, y, w, h, 0)  # Black BG
        pyxel.rectb(x, y, w, h, 7)  # White Border
        pyxel.rect(x, y, w, 15, 1)  # Header
        pyxel.text(x + 50, y + 5, "--- VILLAGE B SHOP ---", 7)
        # Show player's gold in top right
        pyxel.text(x + w - 60, y + 5, f"Gold: {self.player_gold}", 11)
        
        # List items
        list_x = x + 10
        list_y = y + 25
        for i, item in enumerate(self.shop_inventory):
            color = 10 if i == self.cursor else 7
            if i == self.cursor:
                pyxel.rect(list_x - 2, list_y + i*14 - 2, 120, 12, 1)
            
            prefix = "> " if i == self.cursor else "  "
            pyxel.text(list_x, list_y + i*14, f"{prefix}{item['name']}", color)
            pyxel.text(list_x + 80, list_y + i*14, f"{item['price']}G", 11)

        # Item Details Pane
        detail_x = x + 130
        detail_y = y + 25
        pyxel.rectb(detail_x - 5, detail_y - 5, 85, 100, 7)
        
        curr_item = self.shop_inventory[self.cursor]
        pyxel.text(detail_x, detail_y, "[DETAILS]", 6)
        pyxel.text(detail_x, detail_y + 15, curr_item["name"], 10)
        pyxel.text(detail_x, detail_y + 27, f"Type: {curr_item['type']}", 7)
        pyxel.text(detail_x, detail_y + 39, f"Price: {curr_item['price']}G", 11)
        pyxel.text(detail_x, detail_y + 55, curr_item.get("desc", ""), 13)
        
        # Navigation Instructions (always visible)
        pyxel.text(x + 10, y + h - 15, "[Z]: Buy  [X]: Exit  [UP/DOWN]: Select", 6)
        
        # Confirmation Dialog
        if self.confirming:
            # Draw overlay
            cx, cy, cw, ch = 40, 80, 176, 80
            pyxel.rect(cx, cy, cw, ch, 0)
            pyxel.rectb(cx, cy, cw, ch, 10)
            pyxel.rect(cx, cy, cw, 15, 5)
            pyxel.text(cx + 60, cy + 5, "CONFIRM", 7)
            
            item = self.shop_inventory[self.cursor]
            pyxel.text(cx + 10, cy + 25, f"{item['name']} costs", 7)
            pyxel.text(cx + 10, cy + 37, f"{item['price']} Gold.", 11)
            pyxel.text(cx + 10, cy + 52, "Buy this item?", 7)
            pyxel.text(cx + 10, cy + 65, "[Z]: Yes  [X]: No", 6)
