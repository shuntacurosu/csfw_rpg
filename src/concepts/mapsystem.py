from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class LoadedEvent(BaseModel):
    # TODO: Define fields for Loaded
    pass

class MapSystem(Concept):
    """
    Concept: MapSystem
    Emits Events: Loaded
    """
    __events__ = {
        "Loaded": LoadedEvent
    }

    def __init__(self, name: str = "MapSystem"):
        super().__init__(name)
        self.maps = {}
        self.current_map = None
        self.tile_size = 16

    def load(self, payload: dict):
        """
        Action: load
        """
        print(f"MapSystem.load called with {payload}")
        import json
        import os
        map_file_rel = payload.get("map_file")
        
        # Resolve path relative to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        map_file = os.path.join(base_dir, map_file_rel)
        
        if map_file:
            try:
                with open(map_file, 'r') as f:
                    data = json.load(f)
                    for m in data.get("maps", []):
                        self.maps[m["id"]] = m
                    
                    # Set default map (0)
                    if 0 in self.maps:
                        self.current_map = self.maps[0]
                        print("Map 0 loaded successfully")
                        self.emit("Loaded", {"map_id": 0})
            except Exception as e:
                print(f"Failed to load maps: {e}")

    def check_collision(self, payload: dict):
        pass

    def draw(self, payload: dict):
        """
        Action: draw
        """
        # print("MapSystem.draw called") # Debug
        import pyxel
        if not self.current_map:
            # print("No current map to draw")
            return
            
        tiles = self.current_map["tiles"]
        # Simple loop to draw tiles
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                # 0 = Grass (0,0 in sprite sheet), 1 = Wall (16,0)
                # Sprite sheet is 16x16 grid
                u = 0
                v = 0
                if tile == 0: # Grass
                    u = 0
                    v = 0
                elif tile == 1: # Wall
                    u = 16
                    v = 0
                
                pyxel.blt(x * self.tile_size, y * self.tile_size, 0, u, v, 16, 16)


