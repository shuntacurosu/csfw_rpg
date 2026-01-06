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
        Loads pre-generated sprite sheets from assets/images/.
        """
        import pyxel
        import os
        
        # Initialize Pyxel (256x256, title, fps=60)
        pyxel.init(256, 256, title="CSFW RPG", fps=60)
        
        # Load resources
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Load main sprites (Bank 0)
        sprites_path = os.path.join(base_dir, "assets", "images", "sprites.png").replace("\\", "/")
        if os.path.exists(sprites_path):
            pyxel.images[0].load(0, 0, sprites_path)
            print(f"Loaded sprites: {sprites_path}")
        else:
            raise FileNotFoundError(f"Sprite sheet not found: {sprites_path}")
        
        # Load enemy sprites (Bank 1)
        enemies_path = os.path.join(base_dir, "assets", "images", "enemies.png").replace("\\", "/")
        if os.path.exists(enemies_path):
            pyxel.images[1].load(0, 0, enemies_path)
            print(f"Loaded enemies: {enemies_path}")
        else:
            raise FileNotFoundError(f"Enemy sprite sheet not found: {enemies_path}")

        self.emit("Initialized", {})

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

