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
    ROOF = 8 # Red
    
    # -----------------------------------------------
    # Chest Closed (16x16) at (0, 48)
    base_x, base_y = 0, 48
    
    # 1. Clear Area (Make transparent)
    img.rect(base_x, base_y, 16, 16, TRANSPARENT)
    
    # 2. Draw Body
    img.rect(base_x+2, base_y+5, 12, 9, BODY)
    img.rectb(base_x+2, base_y+5, 12, 9, OUTLINE)
    
    # 3. Draw Lid
    img.rect(base_x+1, base_y+3, 14, 3, LID)
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
    
    # 3. Draw Opened Lid
    img.rect(base_x+2, base_y+1, 12, 3, LID)
    img.rectb(base_x+2, base_y+1, 12, 3, OUTLINE)
    
    # 4. Dark Inside
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
        
    # 3. Hilt
    img.line(base_x+4, base_y+12, base_x+2, base_y+14, BODY)
    
    # 4. Guard
    img.line(base_x+8, base_y+9, base_x+5, base_y+12, LOCK)

    # -----------------------------------------------
    # House Exterior (16x16) at (48, 48) -> Tile ID 51
    # (row 3, col 3) => 3*16 + 3 = 51
    base_x, base_y = 48, 48
    img.rect(base_x, base_y, 16, 16, 3) # Fill with Path color (Pink/Brown)
    
    # Roof (Red/Brown)
    img.line(base_x+0, base_y+6, base_x+8, base_y+0, ROOF)
    img.line(base_x+15, base_y+6, base_x+7, base_y+0, ROOF)
    img.rect(base_x+1, base_y+6, 14, 2, ROOF) # Roof bottom
    img.rect(base_x+2, base_y+2, 12, 4, ROOF) # Roof fill
    
    # Walls (White/Beige)
    img.rect(base_x+2, base_y+8, 12, 8, BLADE) # White wall
    img.rectb(base_x+2, base_y+8, 12, 8, OUTLINE) # Outline
    
    # Door (Brown)
    img.rect(base_x+6, base_y+11, 4, 5, BODY)
    img.rectb(base_x+6, base_y+11, 4, 5, OUTLINE)

    print("[ItemAssets] Generated chest, sword, and house sprites at y=48")
