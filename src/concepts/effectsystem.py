from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Optional

class EffectSystem(Concept):
    """
    Concept: EffectSystem
    Handles visual effects like map banners.
    """
    
    def __init__(self, name: str = "EffectSystem"):
        super().__init__(name)
        
        # Banner State
        self.banner_text: str = ""
        self.banner_timer: int = 0
        self.banner_y: float = -20.0
        self.banner_state: str = "IDLE" # IDLE, SLIDE_IN, DISPLAY, SLIDE_OUT
        
    def show_banner(self, payload: dict):
        """Action: show_banner"""
        text = payload.get("text", "")
        if not text: return
        
        self.banner_text = text
        self.banner_timer = 0
        self.banner_state = "SLIDE_IN"
        self.banner_y = -20.0
        
    def draw(self, payload: dict):
        """Action: draw"""
        import pyxel
        
        if self.banner_state == "IDLE":
            return
            
        # Animation Logic
        target_y = 10.0
        start_y = -20.0
        speed = 2.0
        
        if self.banner_state == "SLIDE_IN":
            if self.banner_y < target_y:
                self.banner_y += speed
            else:
                self.banner_y = target_y
                self.banner_state = "DISPLAY"
                self.banner_timer = 90 # 3 seconds at 30fps
                
        elif self.banner_state == "DISPLAY":
            if self.banner_timer > 0:
                self.banner_timer -= 1
            else:
                self.banner_state = "SLIDE_OUT"
                
        elif self.banner_state == "SLIDE_OUT":
            if self.banner_y > start_y:
                self.banner_y -= speed
            else:
                self.banner_state = "IDLE"
                
        # Drawing
        # Reset camera for UI overlay
        old_camera = pyxel.camera(0, 0) # Returns old camera? No, just sets. 
        # Actually pyxel.camera() returns nothing. We rely on draw order.
        
        # Draw Banner Background
        # Center horizontally
        w = len(self.banner_text) * 4 + 20
        screen_w = 256 # Assuming standard width, or get from somewhere
        x = (screen_w - w) // 2
        y = int(self.banner_y)
        
        # Simple style: Black rect with white border
        pyxel.rect(x, y, w, 15, 0)
        pyxel.rectb(x, y, w, 15, 7)
        
        # Text
        text_x = x + 10
        text_y = y + 5
        pyxel.text(text_x, text_y, self.banner_text, 7)
