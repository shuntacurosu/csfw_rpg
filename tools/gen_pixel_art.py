from PIL import Image, ImageDraw
import random
import os

def create_pixel_art():
    # Create 256x256 image with Palette mode
    img = Image.new('P', (256, 256), 0)
    
    # We can setup a dummy palette just so the saved PNG looks okay in viewers
    # But Pyxel only cares about the indices.
    # Pyxel Palette (Approximate for preview)
    palette = [
        0,0,0,          # 0 Black
        29,43,83,       # 1 Dk Blue
        126,37,83,      # 2 Dk Purple
        0,135,81,       # 3 Dk Green
        171,82,54,      # 4 Brown
        95,87,79,       # 5 Dk Gray
        194,195,199,    # 6 Lt Gray
        255,241,232,    # 7 White
        255,0,77,       # 8 Red
        255,163,0,      # 9 Orange
        255,236,39,     # 10 Yellow
        0,228,54,       # 11 Green
        41,173,255,     # 12 Blue
        131,118,156,    # 13 Indigo
        255,119,168,    # 14 Pink
        255,204,170     # 15 Peach
    ]
    # Pad to 768
    palette.extend([0]*(768-len(palette)))
    img.putpalette(palette)
    
    pixels = img.load()

    # Helpers
    def rect(x, y, w, h, col):
        for j in range(h):
            for i in range(w):
                pixels[x+i, y+j] = col

    def noise(x, y, w, h, base_col, secondary_col, prob=0.1):
        for j in range(h):
            for i in range(w):
                if random.random() < prob:
                    pixels[x+i, y+j] = secondary_col
                else:
                    pixels[x+i, y+j] = base_col

    # --- Tiles (Row 0) ---
    # 0: Grass (0,0) - Green(11) with Dark Green(3)
    noise(0, 0, 16, 16, 11, 3, 0.2)
    # Flowers
    pixels[3,3] = 10 # Yellow
    pixels[12,8] = 7 # White

    # 1: Wall (16,0) - Gray(6) with Dk Gray(5) bricks
    rect(16, 0, 16, 16, 13) # Indigo/Grayish base
    # Mortar/Lines
    rect(16, 0, 16, 16, 6) # Lt Gray
    # Bricks
    for j in range(0, 16, 4):
        rect(16, j, 16, 1, 5) # Dark lines
    for j in range(0, 16, 4):
        offset = 0 if (j//4)%2==0 else 8
        rect(16+offset+4, j+1, 1, 3, 5)
        rect(16+offset+12, j+1, 1, 3, 5)
        
    # 2: Water (32,0) - Blue(12) with Lt Blue/White waves
    rect(32, 0, 16, 16, 12)
    pixels[34, 4] = 7; pixels[35, 4] = 7; pixels[36, 4] = 7
    pixels[40, 10] = 7; pixels[41, 10] = 7

    # 3: Path (48,0) - Brown(4) with Orange(9) details
    noise(48, 0, 16, 16, 4, 9, 0.3)

    # --- Characters (Row 1) ---
    # Hero (0,16) -> Red(8)
    # Body
    rect(4, 16+4, 8, 10, 8) # Red Cape/Armor
    rect(5, 16+2, 6, 4, 15) # Face (Peach)
    rect(5, 16+2, 6, 2, 4)  # Hair (Brown)
    # Eyes
    pixels[6, 16+4] = 0
    pixels[9, 16+4] = 0
    # Legs
    rect(5, 16+14, 2, 2, 0)
    rect(9, 16+14, 2, 2, 0)

    # --- NPCs (Row 2) ---
    # Villager (0,32) -> Blue(12) tunic
    rect(4, 32+4, 8, 10, 12) # Blue
    rect(5, 32+2, 6, 4, 15) # Face
    rect(5, 32+2, 6, 2, 10) # Blonde Hair
    pixels[6, 32+4] = 0
    pixels[9, 32+4] = 0
    rect(5, 32+14, 2, 2, 0)
    rect(9, 32+14, 2, 2, 0)

    # Save
    out_path = "assets/images/sprites.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"Generated clean indexed sprites at {out_path}")

if __name__ == "__main__":
    create_pixel_art()
