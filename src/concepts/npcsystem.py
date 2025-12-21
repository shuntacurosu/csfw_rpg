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
        self.npcs = []
        self.active_dialog = None # (text, timer)

    def load(self, payload: dict):
        """
        Action: load
        """
        print(f"NpcSystem.load called with {payload}")
        import json
        import os
        
        # Resolve path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # Use simple path construction
        full_path = os.path.join(base_dir, "assets", "data", "npcs.json")
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r') as f:
                    data = json.load(f)
                    self.npcs = data.get("npcs", [])
                    print(f"Loaded {len(self.npcs)} NPCs")
                    for npc in self.npcs:
                        self.emit("NpcSpawned", npc)
            except Exception as e:
                print(f"Error loading NPCs: {e}")
        else:
            print(f"NPC file not found: {full_path}")


    def check_interaction(self, payload: dict):
        """
        Action: check_interaction
        Reacts to Player.InteractionAttempt
        """
        px = payload.get("x")
        py = payload.get("y")
        pw = payload.get("w", 16)
        ph = payload.get("h", 16)
        
        # Clear dialog if already active (toggle off)
        if self.active_dialog:
            self.active_dialog = None
            return

        # Simple proximity check (center to center distance or overlapping box)
        # Using interaction radius
        p_center_x = px + pw/2
        p_center_y = py + ph/2
        
        for npc in self.npcs:
            nx = npc["x"]
            ny = npc["y"]
            n_center_x = nx + 8
            n_center_y = ny + 8
            
            # Distance
            dist = ((p_center_x - n_center_x)**2 + (p_center_y - n_center_y)**2)**0.5
            if dist < 24: # Less than 1.5 tiles away
                print(f"Interaction with NPC {npc['id']}!")
                text = npc.get("dialog", ["..."])[0] # Just show first line
                self.active_dialog = text
                self.emit("DialogStarted", {"npc_id": npc["id"], "dialog": npc.get("dialog", [])})
                return

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

