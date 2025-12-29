import pyxel

def load_item_sprites():
    """
    Generate item and object sprites into Image Bank 0.
    Target Area: y=48 (Row 3).
    """
    img = pyxel.images[0]
    
    # Colors
    TRANSPARENT = 0
    OUTLINE = 1 # Dark Blue (looks like black)
    BODY = 4 # Brown
    LID = 9 # Orange
    LOCK = 10 # Yellow
    BLADE = 7 # White
    SHADOW = 13 # Gray
    
    # -----------------------------------------------
    # Chest Closed (16x16) at (0, 48)
    base_x, base_y = 0, 48
    
    # 1. Clear Area (Make transparent)
    img.rect(base_x, base_y, 16, 16, TRANSPARENT)
    
    # 2. Draw Body
    # Fill main box
    img.rect(base_x+2, base_y+5, 12, 9, BODY)
    # Outline main box
    img.rectb(base_x+2, base_y+5, 12, 9, OUTLINE)
    
    # 3. Draw Lid (Top part)
    # Fill lid
    img.rect(base_x+1, base_y+3, 14, 3, LID)
    # Outline lid
    img.rectb(base_x+1, base_y+3, 14, 3, OUTLINE)
    
    # 4. Lock
    img.pset(base_x+7, base_y+9, LOCK)
    img.pset(base_x+8, base_y+9, LOCK)
    
    # -----------------------------------------------
    # Chest Opened (16x16) at (16, 48)
    base_x, base_y = 16, 48
    
    # 1. Clear Area
    img.rect(base_x, base_y, 16, 16, TRANSPARENT)

    # 2. Draw Body
    img.rect(base_x+2, base_y+5, 12, 9, BODY)
    img.rectb(base_x+2, base_y+5, 12, 9, OUTLINE)
    
    # 3. Draw Opened Lid (Shifted Up and narrower perspective?)
    # Just draw lid higher up or behind.
    # Let's draw it "open" pointing up/back.
    img.rect(base_x+2, base_y+1, 12, 3, LID)
    img.rectb(base_x+2, base_y+1, 12, 3, OUTLINE)
    
    # 4. Dark Inside
    img.rect(base_x+3, base_y+6, 10, 7, 0) # Use 0 (Transparent) to show floor? 
    # Or use Dark Color (1 or 5) to look like deep shadow?
    # If transparent, it shows floor. Floor is noisy.
    # Better to use black/dark.
    img.rect(base_x+3, base_y+6, 10, 7, 1) # Dark inside

    # -----------------------------------------------
    # Sword (16x16) at (32, 48)
    base_x, base_y = 32, 48
    
    # 1. Clear Area
    img.rect(base_x, base_y, 16, 16, TRANSPARENT)

    # 2. Blade
    for i in range(8):
        img.pset(base_x+12-i, base_y+4+i, BLADE) # Blade
        img.pset(base_x+13-i, base_y+5+i, SHADOW) # Shadow
        
    # Outline for sword? Maybe just edges.
    
    # 3. Hilt
    img.line(base_x+4, base_y+12, base_x+2, base_y+14, BODY)
    
    # 4. Guard
    img.line(base_x+8, base_y+9, base_x+5, base_y+12, LOCK)

    print("[ItemAssets] Generated chest and sword sprites at y=48 with outlines")
