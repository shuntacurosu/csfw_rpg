from cs_framework.core.concept import Concept
from pydantic import BaseModel

class CameraSystem(Concept):
    """
    Concept: CameraSystem
    Manages screen scrolling.
    """
    __events__ = {}

    def __init__(self, name: str = "CameraSystem"):
        super().__init__(name)
        self.cam_x = 0
        self.cam_y = 0
        self.map_w = 256 # Default pixels
        self.map_h = 256
        self.screen_w = 256
        self.screen_h = 256
        
    def set_bounds(self, payload: dict):
        """
        Action: set_bounds
        """
        # tile coords
        mw = payload.get("width", 16)
        mh = payload.get("height", 16)
        self.map_w = mw * 16
        self.map_h = mh * 16
        print(f"Camera bounds set to {self.map_w}x{self.map_h}")

    def follow_player(self, payload: dict):
        """
        Action: follow_player
        """
        px = payload.get("x")
        py = payload.get("y")
        
        # Center player
        target_x = px - self.screen_w // 2 + 8 # +8 for half player size
        target_y = py - self.screen_h // 2 + 8
        
        # Clamp
        self.cam_x = max(0, min(target_x, self.map_w - self.screen_w))
        self.cam_y = max(0, min(target_y, self.map_h - self.screen_h))
        
    def apply(self, payload: dict):
        """
        Action: apply
        Called before draw loop
        """
        import pyxel
        pyxel.camera(self.cam_x, self.cam_y)
