from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class DialogStartedEvent(BaseModel):
    npc_id: int

class DialogEndedEvent(BaseModel):
    npc_id: int

class NpcSpawnedEvent(BaseModel):
    id: int
    name: str = "NPC"
    x: int
    y: int
    sprite_u: int
    sprite_v: int

    
class ItemFoundEvent(BaseModel):
    item: Dict[str, Any]

class NpcSystem(Concept):
    """
    Concept: NpcSystem
    Emits Events: DialogStarted, DialogEnded, NpcSpawned
    """
    __events__ = {
        "DialogStarted": DialogStartedEvent,
        "DialogEnded": DialogEndedEvent,
        "NpcSpawned": NpcSpawnedEvent,
        "ItemFound": ItemFoundEvent
    }

    def __init__(self, name: str = "NpcSystem"):
        super().__init__(name)
        self.npcs = [] # All NPCs data
        self.active_npcs = [] # NPCs on current map
        self.active_dialog = None # Current string to show
        self.current_npc = None # The NPC object being talked to
        self.current_line_index = 0
        # Movement
        self.move_timer = 0
        self.move_interval = 60  # Move every 60 frames (1 second at 60fps)
        self.map_system = None  # Reference to MapSystem for collision
        self.player = None  # Reference to Player for collision

    def set_map_system(self, map_sys):
        """Set reference to MapSystem for collision detection"""
        self.map_system = map_sys

    def set_player(self, player):
        """Set reference to Player for collision detection"""
        self.player = player

    def load(self, payload: dict):
        """Action: load"""
        current_map_id = payload.get("map_id")
        
        if not self.npcs:
             import os
             import json
             base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
             npc_file = os.path.join(base_dir, "assets", "data", "npcs.json")
             
             if os.path.exists(npc_file):
                 with open(npc_file, 'r') as f:
                     data = json.load(f)
                     self.npcs = data.get("npcs", [])
                     print(f"Loaded {len(self.npcs)} total NPCs")
        
        if current_map_id is None:
            current_map_id = 0
            
        self.active_npcs = [npc.copy() for npc in self.npcs if npc.get("map_id") == current_map_id]
        # Store original positions for mobile NPCs
        for npc in self.active_npcs:
            npc["origin_x"] = npc["x"]
            npc["origin_y"] = npc["y"]
        print(f"Active NPCs for Map {current_map_id}: {len(self.active_npcs)}")

        for npc in self.active_npcs:
            self.emit("NpcSpawned", {
                "id": npc["id"],
                "x": npc["x"],
                "y": npc["y"], 
                "sprite_u": npc["sprite_u"],
                "sprite_v": npc["sprite_v"],
                "name": str(npc["id"])
            })

    def check_interaction(self, payload: dict):
        """Action: check_interaction"""
        px = payload.get("x")
        py = payload.get("y")
        
        for npc in self.active_npcs:
            nx, ny = npc["x"], npc["y"]
            dist = ((px - nx)**2 + (py - ny)**2)**0.5
            if dist < 20:
                self.current_npc = npc
                
                # Chest Logic
                if npc.get("is_chest", False):
                    self.current_line_index = 0
                    if not npc.get("opened", False):
                        npc["opened"] = True
                        # Change Sprite to Opened Chest (Next tile)
                        npc["sprite_u"] += 16 
                        
                        item_data = npc.get("item_reward", {"name": "Potion", "type": "item", "value": 1})
                        item_name = item_data.get("name", "Item")
                        
                        dialog_text = f"Found {item_name}!"
                        npc["dialog"] = [dialog_text] # Inject dialog based on item
                        
                        self.active_dialog = dialog_text
                        print(f"Chest opened! Got {item_name}")
                        self.emit("DialogStarted", {"npc_id": npc["id"]})
                        self.emit("ItemFound", {"item": item_data})
                    else:
                        npc["dialog"] = ["It's empty."]
                        self.active_dialog = "It's empty."
                        self.emit("DialogStarted", {"npc_id": npc["id"]})
                    return

                self.current_line_index = 0
                self.active_dialog = npc["dialog"][0]
                print(f"Interacted with NPC {npc['id']}: {self.active_dialog}")
                self.emit("DialogStarted", {"npc_id": npc["id"]})
                return

    def advance_dialog(self, payload: dict):
        """Action: advance_dialog"""
        if not self.current_npc:
            return

        self.current_line_index += 1
        if self.current_line_index >= len(self.current_npc["dialog"]):
            npc_id = self.current_npc["id"]
            self.clear_dialog({})
            self.emit("DialogEnded", {"npc_id": npc_id})
        else:
            self.active_dialog = self.current_npc["dialog"][self.current_line_index]
            print(f"Dialog advanced: {self.active_dialog}")

    def clear_dialog(self, payload: dict):
        """Action: clear_dialog"""
        self.active_dialog = None
        self.current_npc = None
        self.current_line_index = 0

    def update(self, payload: dict):
        """Action: update - Move mobile NPCs periodically"""
        import random
        
        self.move_timer += 1
        if self.move_timer < self.move_interval:
            return
        
        self.move_timer = 0
        
        for npc in self.active_npcs:
            # Skip non-mobile NPCs
            if not npc.get("mobile", False):
                continue
            
            # Skip if this NPC is in conversation
            if self.current_npc and self.current_npc["id"] == npc["id"]:
                continue
            
            # Random movement direction
            dx = random.choice([-8, 0, 0, 8])  # More likely to stay still
            dy = random.choice([-8, 0, 0, 8])
            
            if dx == 0 and dy == 0:
                continue
            
            new_x = npc["x"] + dx
            new_y = npc["y"] + dy
            
            # Limit movement range from origin (32px radius)
            origin_x = npc.get("origin_x", npc["x"])
            origin_y = npc.get("origin_y", npc["y"])
            max_range = 32
            
            if abs(new_x - origin_x) > max_range or abs(new_y - origin_y) > max_range:
                continue
            
            # Basic bounds check (stay on screen)
            if not (0 <= new_x <= 240 and 0 <= new_y <= 200):
                continue
            
            # Collision check with map tiles
            if self._is_walkable(new_x, new_y):
                npc["x"] = new_x
                npc["y"] = new_y

    def _is_walkable(self, x, y):
        """Check if position is walkable (not wall/water/mountain/player)"""
        # Check player collision first
        if self.player:
            px = self.player.x
            py = self.player.y
            # Simple box collision (both are 16x16)
            if (x < px + 16 and x + 16 > px and
                y < py + 16 and y + 16 > py):
                return False
        
        if not self.map_system:
            return True  # No map reference, allow movement
        
        current_map = self.map_system.map_data.get(self.map_system.current_map_id)
        if not current_map:
            return True
        
        tiles = current_map.get("tiles", [])
        map_w = current_map.get("width", 16)
        map_h = current_map.get("height", 16)
        
        # Check all 4 corners of the NPC (16x16 sprite)
        margin = 4
        points = [
            (x + margin, y + margin),
            (x + 16 - margin, y + margin),
            (x + margin, y + 16 - margin),
            (x + 16 - margin, y + 16 - margin)
        ]
        
        for px, py in points:
            tx = int(px // 16)
            ty = int(py // 16)
            
            if tx < 0 or tx >= map_w or ty < 0 or ty >= map_h:
                return False
            
            tile_id = tiles[ty][tx]
            # Block tiles: 1=Wall, 2=Water, 6=Mountain
            if tile_id in [1, 2, 6]:
                return False
        
        return True

    def draw(self, payload: dict):
        """Action: draw"""
        import pyxel
        
        for npc in self.active_npcs:
             if npc.get("is_chest"):
                 # Chest Logic: Open vs Closed
                 # Using Item Assets (generated at y=48)
                 # Closed: u=0, v=48
                 # Opened: u=16, v=48
                 u = 16 if npc.get("opened") else 0
                 v = 48
                 pyxel.blt(npc["x"], npc["y"], 0, u, v, 16, 16, 0)
             else:
                 u = npc.get("sprite_u", 0)
                 v = npc.get("sprite_v", 32)
                 # Use color 0 (black) as transparent
                 # Sprites must have black (color 0) backgrounds to be transparent
                 pyxel.blt(npc["x"], npc["y"], 0, u, v, 16, 16, 0)
        
        if self.active_dialog:
             # Draw box at bottom
             # Screen is typically 256x256
             box_y = 210
             pyxel.rect(10, box_y, 236, 40, 0)
             pyxel.rectb(10, box_y, 236, 40, 7)
             pyxel.text(14, box_y + 4, self.active_dialog, 7)
             
             # Small indicator for next line
             if pyxel.frame_count % 30 < 15:
                 pyxel.text(236, box_y + 30, ">", 7)

