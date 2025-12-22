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

class NpcSystem(Concept):
    """
    Concept: NpcSystem
    Emits Events: DialogStarted, DialogEnded, NpcSpawned
    """
    __events__ = {
        "DialogStarted": DialogStartedEvent,
        "DialogEnded": DialogEndedEvent,
        "NpcSpawned": NpcSpawnedEvent
    }

    def __init__(self, name: str = "NpcSystem"):
        super().__init__(name)
        self.npcs = [] # All NPCs data
        self.active_npcs = [] # NPCs on current map
        self.active_dialog = None # Current string to show
        self.current_npc = None # The NPC object being talked to
        self.current_line_index = 0

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
            
        self.active_npcs = [npc for npc in self.npcs if npc.get("map_id") == current_map_id]
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

    def draw(self, payload: dict):
        """Action: draw"""
        import pyxel
        
        for npc in self.active_npcs:
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

