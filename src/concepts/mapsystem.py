from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class LoadedEvent(BaseModel):
    # TODO: Define fields for Loaded
    pass

class MoveValidEvent(BaseModel):
    x: float
    y: float

class MapSystem(Concept):
    """
    Concept: MapSystem
    Emits Events: MoveValid
    """
    __events__ = {
        "MoveValid": MoveValidEvent
    }

    def __init__(self, name: str = "MapSystem"):
        super().__init__(name)
        self.map_data = {}
        self.current_map_id = 0
        self.dynamic_obstacles = [] # List of {x,y, w, h}

    def load(self, payload: dict):
        """
        Action: load
        """
        print(f"MapSystem.load called with {payload}")
        import os
        import json
        map_file = payload.get("map_file", "assets/data/maps.json")
        
        # Simple path fix
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_dir, map_file)

        if os.path.exists(full_path):
             with open(full_path, 'r') as f:
                 data = json.load(f)
                 self.map_data = {m["id"]: m for m in data.get("maps", [])}
                 print(f"Map {self.current_map_id} loaded successfully")
        else:
             print(f"Map file not found: {full_path}")

    def validate_move(self, payload: dict):
        """
        Action: validate_move
        Checks if the target position is walkable.
        """
        x = payload.get("x")
        y = payload.get("y")
        
        # Player size is 16x16. Check corners or center?
        # Let's check center and corners.
        # Reduced hitbox for forgiveness.
        margin = 4
        points = [
            (x + margin, y + margin),
            (x + 16 - margin, y + margin),
            (x + margin, y + 16 - margin),
            (x + 16 - margin, y + 16 - margin)
        ]
        
        current_map = self.map_data.get(self.current_map_id)
        if not current_map:
            return 

        is_valid = True
        
        # Check dynamic obstacles (simple box)
        # Player box: x, y, 16, 16 (approx)
        ph_x = x + 4
        ph_y = y + 4
        ph_w = 8
        ph_h = 8
        
        for obs in self.dynamic_obstacles:
            ox = obs.get("x")
            oy = obs.get("y")
            # Assume 16x16 for now if not specified
            ow = obs.get("w", 16)
            oh = obs.get("h", 16)
            
            # AABB check
            if (ph_x < ox + ow and
                ph_x + ph_w > ox and
                ph_y < oy + oh and
                ph_y + ph_h > oy):
                is_valid = False
                break
        
        if not is_valid: return

        tiles = current_map["tiles"]
        
        for px, py in points:
            # Convert pixel to tile coords
            tx = int(px // 16)
            ty = int(py // 16)
            
            # Bounds check
            if tx < 0 or tx >= 16 or ty < 0 or ty >= 16:
                is_valid = False
                break
                
            tile_id = tiles[ty][tx]
            
            # Define walkable tiles
            # 0: Grass, 3: Path. 
            # 1: Wall (Block), 2: Water (Block)
            if tile_id in [1, 2]: 
                is_valid = False
                break
        
        if is_valid:
            self.emit("MoveValid", {"x": x, "y": y})

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


