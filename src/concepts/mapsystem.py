from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class MapLoadedEvent(BaseModel):
    map_id: int
    width: int
    height: int
    map_name: str

class MoveValidEvent(BaseModel):
    x: float
    y: float

class BattleStartedEvent(BaseModel):
    enemies: Any # List of enemy IDs

class MapSystem(Concept):
    """
    Concept: MapSystem
    Emits Events: MoveValid, MapLoaded, BattleStarted
    """
    __events__ = {
        "MoveValid": MoveValidEvent,
        "MapLoaded": MapLoadedEvent,
        "BattleStarted": BattleStartedEvent 
    }

    def __init__(self, name: str = "MapSystem"):
        super().__init__(name)
        self.map_data = {}
        self.current_map_id = 0
        self.dynamic_obstacles = []
        self.npc_system = None  # Reference to NpcSystem for live collision
        self.last_check_pos = (-1, -1)

    def set_npc_system(self, npc_sys):
        """Set reference to NpcSystem for live NPC collision detection"""
        self.npc_system = npc_sys 

    def load(self, payload: dict):
        """
        Action: load
        """
        import os
        import json
        
        target_id = payload.get("map_id")
        
        # Helper to get current map data if available
        def get_map_dims(mid):
            if mid in self.map_data:
                return self.map_data[mid].get("width", 16), self.map_data[mid].get("height", 16)
            return 16, 16

        def get_map_name(mid):
            if mid in self.map_data:
                return self.map_data[mid].get("name", f"Map {mid}")
            return f"Map {mid}"

        # Logic for switch vs initial load...
        # If target_id is present, we assume data is loaded. 
        if target_id is not None:
             self.current_map_id = target_id
             self.dynamic_obstacles = [] 
             w, h = get_map_dims(self.current_map_id)
             map_name = get_map_name(self.current_map_id)
             self.emit("MapLoaded", {"map_id": self.current_map_id, "width": w, "height": h, "map_name": map_name})
             print(f"Switched to Map {self.current_map_id} ({map_name})")
             return

        print(f"MapSystem.load called with {payload}")
        map_file = payload.get("map_file", "assets/data/maps.json")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_dir, map_file)

        if os.path.exists(full_path):
             with open(full_path, 'r') as f:
                 data = json.load(f)
                 self.map_data = {m["id"]: m for m in data.get("maps", [])}
                 # Initial load emit
                 w, h = get_map_dims(self.current_map_id)
                 map_name = get_map_name(self.current_map_id)
                 print(f"Map {self.current_map_id} loaded. Name: {map_name} Size: {w}x{h}")
                 self.emit("MapLoaded", {"map_id": self.current_map_id, "width": w, "height": h, "map_name": map_name})
        else:
             print(f"Map file not found: {full_path}")

    def validate_move(self, payload: dict):
        """
        Action: validate_move
        Checks tiles and portals.
        """
        x = payload.get("x")
        y = payload.get("y")
        
        # Portal Check (Center point)
        px = int((x + 8) // 16)
        py = int((y + 8) // 16)
        
        current_map = self.map_data.get(self.current_map_id)
        if not current_map: return

        portals = current_map.get("portals", [])
        for portal in portals:
            print(f"DEBUG: Check Portal Player({px},{py}) vs Portal({portal['x']},{portal['y']})")
            if portal["x"] == px and portal["y"] == py:
                print(f"Portal Triggered! To Map {portal['target_map']} at {px},{py}")
                # Switch Map
                self.load({"map_id": portal["target_map"]})
                
                # Teleport Player
                tx = portal["target_x"] * 16
                ty = portal["target_y"] * 16
                self.emit("MoveValid", {"x": tx, "y": ty})
                return

        # ... (Rest of collision logic) ...
        # Reduced hitbox for forgiveness.
        margin = 4
        points = [
            (x + margin, y + margin),
            (x + 16 - margin, y + margin),
            (x + margin, y + 16 - margin),
            (x + 16 - margin, y + 16 - margin)
        ]
        
        is_valid = True
        
        # Check NPC collision (live positions from NpcSystem)
        ph_x = x + 4
        ph_y = y + 4
        ph_w = 8
        ph_h = 8
        
        # Use live NPC positions instead of cached obstacles
        if self.npc_system:
            for npc in self.npc_system.active_npcs:
                ox = npc.get("x", 0)
                oy = npc.get("y", 0)
                ow = 16
                oh = 16
                
                if (ph_x < ox + ow and
                    ph_x + ph_w > ox and
                    ph_y < oy + oh and
                    ph_y + ph_h > oy):
                    is_valid = False
                    break
        
        if not is_valid: return

        tiles = current_map["tiles"]
        map_w = current_map.get("width", 16)
        map_h = current_map.get("height", 16)
        
        for px, py in points:
            tx = int(px // 16)
            ty = int(py // 16)
            
            if tx < 0 or tx >= map_w or ty < 0 or ty >= map_h:
                is_valid = False
                break
                
            tile_id = tiles[ty][tx]
            
            # Walkable check (Adjusted for World Map tiles)
            # 0=Grass, 3=Path, 4=Forest, 5=Desert, 7=Village -> Walkable
            # 1=Wall, 2=Water, 6=Mountain -> Block
            if tile_id in [1, 2, 6]: 
                is_valid = False
                break
        
        if is_valid:
            self.emit("MoveValid", {"x": x, "y": y})

    def check_encounter(self, payload: dict):
        """
        Action: check_encounter
        """
        import random
        x = payload.get("x")
        y = payload.get("y")
        
        current_map = self.map_data.get(self.current_map_id)
        if not current_map: return
        
        # Get Rules from Map Data
        rules = current_map.get("encounter_rules", [])
        
        # Fallback to old simple rate if no rules defined (compatibility)
        if not rules:
            base_rate = current_map.get("encounter_rate", 0.0)
            if base_rate > 0 and random.random() < base_rate:
                 self.emit("BattleStarted", {"enemies": ["Slime"]})
            return

        # Player Tile Logic
        tx = int((x + 8) // 16)
        ty = int((y + 8) // 16)
        map_w = current_map.get("width", 16)
        map_h = current_map.get("height", 16)
        
        tile_id = 0
        if 0 <= tx < map_w and 0 <= ty < map_h:
            tile_id = current_map["tiles"][ty][tx]
            
        # Prevent multi-check on same tile (debounce)
        if self.last_check_pos == (tx, ty):
            return
        self.last_check_pos = (tx, ty)
            
        # Evaluate Rules
        # We check specific rules first, then global. Or just check all valid ones?
        # Let's say we find the FIRST matching rule that triggers.
        
        for rule in rules:
            rule_type = rule.get("type", "global")
            rate = rule.get("rate", 0.0)
            
            is_match = False
            
            if rule_type == "global":
                is_match = True
            elif rule_type == "tile":
                target_tiles = rule.get("tile_ids", [])
                if tile_id in target_tiles:
                    is_match = True
            elif rule_type == "rect":
                rx = rule.get("x", 0)
                ry = rule.get("y", 0)
                rw = rule.get("w", 0)
                rh = rule.get("h", 0)
                # Check rect in tile coordinates or pixel coordinates? 
                # Let's assume tile coordinates for ease of editing usually, but pixels are more precise.
                # Given json ease, tile coords are better.
                if rx <= tx < rx + rw and ry <= ty < ry + rh:
                    is_match = True
                    
            if is_match:
                if random.random() < rate:
                    enemies = rule.get("enemies", ["Slime"])
                    # Pick random enemy from list? Or all? Usually random one or group.
                    # Current battle system takes list of enemies. 
                    # If list has multiple, do we spawn all? Or pick one?
                    # Let's assume the list defines the "Troop" or allow picking 1-3.
                    # For now, pass all defined in the list as the encounter group.
                    self.emit("BattleStarted", {"enemies": enemies})
                    return # Encounter triggered, stop checking
                
                # If matched but didn't trigger rate, should we continue to other rules?
                # Usually no. If you are in a "Forest" rule, you shouldn't fall back to "Global" 
                # unless explicitly designed. 
                # Let's assume priority: first matching rule consumes the check.
                return

    def register_obstacle(self, payload: dict):
        """
        Action: register_obstacle
        """
        print(f"Registered obstacle: {payload}")
        self.dynamic_obstacles.append(payload)

    def draw(self, payload: dict):
        """
        Action: draw
        """
        import pyxel
        current_map = self.map_data.get(self.current_map_id)
        if not current_map:
            return
            
        tiles = current_map["tiles"]
        # Simple loop to draw tiles
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                # 0 = Grass (0,0), 1 = Wall (16,0), 2 = Water (32,0), 3 = Path (48,0)
                # Sprite sheet is 16x16 grid. My gen_pixel_art.py put them in a row.
                u = tile * 16
                v = 0
                
                # Check bounds inside sprite sheet (256 width) just in case
                if u >= 256: u = 0
                
                pyxel.blt(x * 16, y * 16, 0, u, v, 16, 16)

        # Draw Portals (Visual Indicators)
        portals = current_map.get("portals", [])
        for portal in portals:
            tx = portal.get("x")
            ty = portal.get("y")
            target_map = portal.get("target_map")
            
            x = tx * 16
            y = ty * 16
            
            # Dungeon Entrance (To Map 10, 11, 12)
            if target_map in [10, 11, 12]:
                # Draw Cave Entrance
                pyxel.rect(x + 3, y + 3, 10, 10, 0) # Black hole
                pyxel.rectb(x + 2, y + 2, 12, 12, 4) # Frame
                
            # Exit to World (To Map 1) from Dungeon (Map 10-12)
            elif target_map == 1 and self.current_map_id in [10, 11, 12]:
                # Draw Stairs Up
                pyxel.rect(x + 3, y + 3, 10, 10, 13) # Gray base
                pyxel.rect(x + 5, y + 5, 6, 6, 7)  # White steps


