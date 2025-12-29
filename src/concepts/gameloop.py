from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class UpdateEvent(BaseModel):
    # TODO: Define fields for Update
    pass

class DrawEvent(BaseModel):
    # TODO: Define fields for Draw
    pass

class GameLoop(Concept):
    """
    Concept: GameLoop
    Emits Events: Update, Draw
    """
    __events__ = {
        "Update": UpdateEvent,
        "Draw": DrawEvent
    }

    def __init__(self, name: str = "GameLoop"):
        super().__init__(name)

    def init(self, payload: dict):
        """
        Action: init
        """
        import pyxel
        import os
        # Initialize Pyxel (256x256, title, fps=60)
        pyxel.init(256, 256, title="CSFW RPG", fps=60)
        # Load resources
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # Pyxel sometimes prefers forward slashes or might struggle with mixed
        img_path = os.path.join(base_dir, "assets", "images", "sprites.png")
        # Normalize to forward slashes for Pyxel
        img_path = img_path.replace("\\", "/")
        print(f"Loading sprite from: {img_path} (Exists: {os.path.exists(img_path)})")
        
        # Initialize with fallback assets FIRST, so if load fails we still have something
        self._create_fallback_assets()
        
        if os.path.exists(img_path):
             try:
                 # Use current API
                 pyxel.images[0].load(0, 0, img_path)
                 print("Attempted load. If successful, sprites are updated.")
             except Exception as e:
                 print(f"Pyxel load error: {e}")
                 # Fallback already in place
        else:
             print(f"Warning: Sprite sheet not found at {img_path}")
             # Fallback already in place
        
        # Generate/Load Programmatic Assets
        print("DEBUG: Starting asset generation...")
        try:
            from concepts.enemy_assets import load_enemy_assets
            load_enemy_assets()
            print("DEBUG: Enemy sprites loaded.")
            
            from concepts.item_assets import load_item_sprites
            load_item_sprites()
            print("DEBUG: Item sprites loaded.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Asset Generation Error: {e}")

        self.emit("Initialized", {})

    def _create_fallback_assets(self):
        import pyxel
        print("Creating fallback assets...")
        # 0: Grass (Green) at 0,0
        pyxel.images[0].rect(0, 0, 16, 16, 11)
        # 1: Wall (Brown) at 16,0
        pyxel.images[0].rect(16, 0, 16, 16, 4)
        # Hero (Red) at 0,16
        pyxel.images[0].rect(0, 16, 16, 16, 8)

    def run(self, payload: dict):
        """
        Action: run
        """
        import pyxel
        pyxel.run(self._update_wrapper, self._draw_wrapper)

    def _update_wrapper(self):
        # This method is called by Pyxel every frame
        # Process pending events to reduce latency (input -> move -> collision)
        # We loop a fixed number of times to handle causal chains within the frame
        # independently of the queue size access which caused a crash.
        # process_events() is safe to call even if empty.
        limit = 5
        if hasattr(self, "runner") and self.runner:
            for _ in range(limit):
                self.runner.process_events()
        
        # Then emit update
        self.emit("Update", {})
        
    def _draw_wrapper(self):
        # Clear screen
        import pyxel
        pyxel.cls(0)
        
        # Emit Draw
        self.emit("Draw", {})
        
        # Process any immediate draw events
        if hasattr(self, "runner") and self.runner:
             # Just one pass related to draw
             self.runner.process_events()

    def update(self, payload: dict):
        # This might be redundant if we use _update_wrapper to emit.
        # However, update action might be used for other things?
        # For now, GameLoop duties are driven by Pyxel.
        pass

    def draw(self, payload: dict):
        pass

