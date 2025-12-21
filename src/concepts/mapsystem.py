from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class MapLoadedEvent(BaseModel):
    map_id: int
    width: int
    height: int

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

        # Logic for switch vs initial load...
        # If target_id is present, we assume data is loaded. 
        if target_id is not None:
             self.current_map_id = target_id
             self.dynamic_obstacles = [] 
             w, h = get_map_dims(self.current_map_id)
             self.emit("MapLoaded", {"map_id": self.current_map_id, "width": w, "height": h})
             print(f"Switched to Map {self.current_map_id}")
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
                 print(f"Map {self.current_map_id} loaded. Size: {w}x{h}")
                 self.emit("MapLoaded", {"map_id": self.current_map_id, "width": w, "height": h})
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
            if portal["x"] == px and portal["y"] == py:
                print(f"Portal Triggered! To Map {portal['target_map']}")
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
        
        # Check dynamic obstacles (simple box)
        ph_x = x + 4
        ph_y = y + 4
        ph_w = 8
        ph_h = 8
        
        for obs in self.dynamic_obstacles:
            ox = obs.get("x")
            oy = obs.get("y")
            ow = obs.get("w", 16)
            oh = obs.get("h", 16)
            
            if (ph_x < ox + ow and
                ph_x + ph_w > ox and
                ph_y < oy + oh and
                ph_y + ph_h > oy):
                is_valid = False
                break
        
        if not is_valid: return

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
        # print(f"MapSystem: check_encounter called with {payload}")
        x = payload.get("x")
        y = payload.get("y")
        
        current_map = self.map_data.get(self.current_map_id)
        if not current_map: return
        
        # Base rate
        base_rate = current_map.get("encounter_rate", 0.0)
        # print(f"[MapSystem] check_encounter for Map {self.current_map_id}. Base Rate: {base_rate}")
        if base_rate <= 0: return

        # Tile Type Modifiers
        tx = int((x + 8) // 16)
        ty = int((y + 8) // 16)
        tiles = current_map["tiles"]
        
        map_w = current_map.get("width", 16)
        map_h = current_map.get("height", 16)
        
        if ty < 0 or ty >= map_h or tx < 0 or tx >= map_w: return
        
        tile_id = tiles[ty][tx]
        
        # 4=Forest, 5=Desert -> High Rate
        # 0=Grass, 3=Path -> Low Rate
        # 7=Village -> Safe
        
        chance = 0.0
        enemies = []
        
        if tile_id in [4]: # Forest
            chance = 0.005 # ~5% per move
            enemies = ["Wolf", "Spider"]
        elif tile_id in [5]: # Desert
            chance = 0.005
            enemies = ["Scorpion", "Snake"]
        elif tile_id in [0, 3]: # Plains/Path
            chance = 0.001 
            enemies = ["Slime", "Bat"]
        elif tile_id == 7: # Village Icon
            chance = 0.0
        else:
            chance = 0.001
            enemies = ["Slime"]
            
        if random.random() < chance:
            self.emit("BattleStarted", {"enemies": enemies})
        else:
            # print(f"Encounter Check: Map {self.current_map_id} Pos ({tx},{ty}) Tile {tile_id} - Chance {chance} - Failed")
            pass

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


