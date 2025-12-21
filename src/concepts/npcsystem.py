from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class DialogstartedEvent(BaseModel):
    # TODO: Define fields for DialogStarted
    pass

class NpcSpawnedEvent(BaseModel):
    id: int
    name: str = "NPC" # Default value since JSON doesn't have it
    x: int
    y: int
    sprite_u: int
    sprite_v: int

class NpcSystem(Concept):
    """
    Concept: NpcSystem
    Emits Events: DialogStarted
    """
    __events__ = {
        "DialogStarted": DialogstartedEvent,
        "NpcSpawned": NpcSpawnedEvent
    }

    def __init__(self, name: str = "NpcSystem"):
        super().__init__(name)
        self.npcs = [] # All NPCs data
        self.active_npcs = [] # NPCs on current map
        self.active_dialog = None # (text, timer)

    def load(self, payload: dict):
        """
        Action: load
        """
        print(f"NpcSystem.load called with {payload}")
        
        # If map_id is provided, filter active NPCs
        current_map_id = payload.get("map_id")
        
        if not self.npcs:
             # Initial load of data
             import os
             import json
             base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
             npc_file = os.path.join(base_dir, "assets", "data", "npcs.json")
             
             if os.path.exists(npc_file):
                 with open(npc_file, 'r') as f:
                     self.npcs = json.load(f)
        
        # Filter for current map
        # Default to map 0 if not specified (initial load)
        if current_map_id is None:
            current_map_id = 0
            
        self.active_npcs = [npc for npc in self.npcs if npc["map_id"] == current_map_id]
        print(f"Loaded {len(self.active_npcs)} NPCs for Map {current_map_id}")

        # Emit spawn events for collision
        for npc in self.active_npcs:
            self.emit("NpcSpawned", {
                "id": npc["id"], # Added id for NpcSpawnedEvent
                "x": npc["x"],
                "y": npc["y"], 
                "sprite_u": npc["sprite_u"], # Added sprite_u for NpcSpawnedEvent
                "sprite_v": npc["sprite_v"], # Added sprite_v for NpcSpawnedEvent
                "name": str(npc["id"])
            })


    def update(self, payload: dict):
        pass

    def draw(self, payload: dict):
        """
        Action: draw
        """
        import pyxel
        for npc in self.npcs:
             # Draw NPC using sprite coordinates
             # Default fallback is Villager (0, 32)
             u = npc.get("sprite_u", 0)
             v = npc.get("sprite_v", 32)
             pyxel.blt(npc["x"], npc["y"], 0, u, v, 16, 16, 0)
        
        # Draw Dialog Box if active
        if self.active_dialog:
            # Draw box at bottom
            pyxel.rect(10, 200, 236, 40, 0) # Black bg
            pyxel.rectb(10, 200, 236, 40, 7) # White border
            pyxel.text(14, 204, self.active_dialog, 7)
        
        # Check for dialog overlay (simple debug for now, or if GameState handles it)
        #Ideally GameState or UiSystem handles dialog rendering. 
        pass

