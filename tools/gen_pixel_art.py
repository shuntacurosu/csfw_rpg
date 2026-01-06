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

    # 4: Forest (64,0) - Dark Green trees
    rect(64, 0, 16, 16, 3) # Base Dk Green
    noise(64, 0, 16, 16, 3, 11, 0.4) # Add lighter green leaves
    # Tree trunks?
    rect(64+7, 12, 2, 4, 4) # Brown trunk

    # 5: Desert (80,0) - Yellow/Orange sand
    rect(80, 0, 16, 16, 10) # Yellow base
    noise(80, 0, 16, 16, 10, 9, 0.2) # Orange specks

    # 6: Mountain (96,0) - Grey peaks
    rect(96, 0, 16, 16, 5) # Dk Gray base
    # Peak
    for i in range(8):
        rect(96+8-i, 2+i, i*2+1, 14-i, 6) # Lt Gray mountain shape
    rect(96+7, 2, 2, 3, 7) # Snowy cap

    # 7: Village Icon (112, 0) - For World Map
    # Background is transparent (0) so ground shows through
    rect(112, 0, 16, 16, 0) # Transparent bg
    rect(112+4, 4, 8, 8, 4) # House body
    rect(112+3, 3, 10, 2, 8) # Red roof

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

    # Shop Keeper (16,32) -> Yellow(10) apron
    rect(16+4, 32+4, 8, 10, 10) # Yellow apron
    rect(16+5, 32+2, 6, 4, 15) # Face
    rect(16+5, 32+2, 6, 2, 4) # Brown Hair
    pixels[16+6, 32+4] = 0
    pixels[16+9, 32+4] = 0
    rect(16+5, 32+14, 2, 2, 0)
    rect(16+9, 32+14, 2, 2, 0)
    # Gold coin indicator
    pixels[16+11, 32+7] = 9  # Orange coin
    pixels[16+12, 32+8] = 9

    # Female Villager (32,32) -> Pink(14)
    rect(32+4, 32+4, 8, 10, 14) # Pink dress
    rect(32+5, 32+2, 6, 4, 15) # Face
    rect(32+4, 32+2, 8, 2, 4) # Long brown hair
    pixels[32+6, 32+4] = 0
    pixels[32+9, 32+4] = 0
    rect(32+5, 32+14, 2, 2, 0)
    rect(32+9, 32+14, 2, 2, 0)

    # Soldier (48,32) -> Dk Blue(1) armor
    rect(48+4, 32+4, 8, 10, 1) # Dark blue armor
    rect(48+5, 32+2, 6, 4, 15) # Face
    rect(48+4, 32+1, 8, 2, 6) # Silver helmet
    pixels[48+6, 32+4] = 0
    pixels[48+9, 32+4] = 0
    rect(48+5, 32+14, 2, 2, 1)
    rect(48+9, 32+14, 2, 2, 1)

    # Mage (64,32) -> Purple(2)
    rect(64+4, 32+4, 8, 10, 2) # Purple robe
    rect(64+5, 32+2, 6, 4, 15) # Face
    rect(64+4, 32+1, 8, 3, 2) # Hood
    pixels[64+6, 32+4] = 0
    pixels[64+9, 32+4] = 0
    rect(64+5, 32+14, 2, 2, 0)
    rect(64+9, 32+14, 2, 2, 0)
    # Staff indicator
    pixels[64+12, 32+6] = 4
    pixels[64+12, 32+7] = 4
    pixels[64+12, 32+8] = 4

    # Elder (80,32) -> White(7) robe, gray hair
    rect(80+4, 32+4, 8, 10, 7) # White robe
    rect(80+5, 32+2, 6, 4, 15) # Face
    rect(80+5, 32+2, 6, 2, 6) # Gray hair
    pixels[80+6, 32+4] = 0
    pixels[80+9, 32+4] = 0
    rect(80+5, 32+14, 2, 2, 0)
    rect(80+9, 32+14, 2, 2, 0)

    # Child (96,32) -> Green(11) smaller
    rect(96+5, 32+6, 6, 8, 11) # Green tunic, smaller
    rect(96+6, 32+4, 4, 3, 15) # Face
    rect(96+6, 32+4, 4, 1, 4) # Hair
    pixels[96+7, 32+5] = 0
    pixels[96+8, 32+5] = 0
    rect(96+6, 32+14, 2, 2, 0)
    rect(96+8, 32+14, 2, 2, 0)

    # Merchant2 (112,32) -> Orange(9) clothes
    rect(112+4, 32+4, 8, 10, 9) # Orange outfit
    rect(112+5, 32+2, 6, 4, 15) # Face
    rect(112+5, 32+2, 6, 2, 5) # Dark gray hair
    pixels[112+6, 32+4] = 0
    pixels[112+9, 32+4] = 0
    rect(112+5, 32+14, 2, 2, 0)
    rect(112+9, 32+14, 2, 2, 0)

    # --- Monsters (Row 3) ---
    # Slime (0,48) -> Green(11)
    rect(4, 48+6, 8, 8, 11) # Green body
    rect(3, 48+8, 10, 6, 11) # Base
    pixels[5, 48+8] = 0
    pixels[10, 48+8] = 0
    # Shine
    pixels[5, 48+7] = 7

    # Skeleton (16,48) -> White(7)/Gray
    rect(16+5, 48+2, 6, 6, 7) # Skull
    rect(16+5, 48+8, 6, 6, 7) # Ribcage
    rect(16+5, 48+14, 2, 2, 7) # Feet
    rect(16+9, 48+14, 2, 2, 7)
    # Eye sockets
    pixels[16+6, 48+4] = 0
    pixels[16+9, 48+4] = 0
    # Mouth
    rect(16+6, 48+6, 4, 1, 0)

    # Ghost (32,48) -> Lt Gray(6) transparent look
    rect(32+4, 48+4, 8, 10, 6) # Body
    rect(32+3, 48+6, 10, 6, 6) # Wider middle
    # Wispy bottom
    pixels[32+3, 48+14] = 6
    pixels[32+5, 48+14] = 6
    pixels[32+7, 48+14] = 6
    pixels[32+9, 48+14] = 6
    pixels[32+11, 48+14] = 6
    # Eyes
    pixels[32+6, 48+7] = 0
    pixels[32+9, 48+7] = 0

    # Bat (48,48) -> Dk Purple(2)
    rect(48+6, 48+6, 4, 4, 2) # Body
    # Wings
    rect(48+2, 48+7, 4, 3, 2)
    rect(48+10, 48+7, 4, 3, 2)
    # Eyes
    pixels[48+7, 48+7] = 8
    pixels[48+8, 48+7] = 8

    # Goblin (64,48) -> Green(3)
    rect(64+4, 48+4, 8, 10, 3) # Dark green body
    rect(64+5, 48+2, 6, 4, 11) # Light green face
    rect(64+4, 48+2, 2, 2, 3) # Ears
    rect(64+10, 48+2, 2, 2, 3)
    pixels[64+6, 48+4] = 0
    pixels[64+9, 48+4] = 0
    rect(64+5, 48+14, 2, 2, 0)
    rect(64+9, 48+14, 2, 2, 0)

    # Orc (80,48) -> Dk Green(3) larger
    rect(80+3, 48+3, 10, 11, 3) # Dark green body
    rect(80+4, 48+2, 8, 5, 11) # Face
    pixels[80+5, 48+4] = 0
    pixels[80+10, 48+4] = 0
    # Tusks
    pixels[80+5, 48+6] = 7
    pixels[80+10, 48+6] = 7
    rect(80+4, 48+14, 3, 2, 0)
    rect(80+9, 48+14, 3, 2, 0)

    # Dragon (96,48) -> Red(8) head
    rect(96+4, 48+3, 8, 8, 8) # Red head
    rect(96+3, 48+4, 10, 6, 8) # Wider
    # Eyes
    pixels[96+5, 48+5] = 10
    pixels[96+10, 48+5] = 10
    # Nostrils
    pixels[96+6, 48+8] = 0
    pixels[96+9, 48+8] = 0
    # Horns
    pixels[96+4, 48+2] = 9
    pixels[96+11, 48+2] = 9
    # Flames from mouth
    rect(96+6, 48+10, 4, 4, 9)
    pixels[96+7, 48+12] = 10
    pixels[96+8, 48+12] = 10

    # Boss Eye (112,48) -> Purple(13) icon
    rect(112+3, 48+3, 10, 10, 13) # Indigo base
    rect(112+5, 48+5, 6, 6, 8) # Red iris
    rect(112+7, 48+7, 2, 2, 0) # Black pupil
    pixels[112+6, 48+6] = 7 # Highlight

    # Save
    out_path = "assets/images/sprites.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"Generated clean indexed sprites at {out_path}")

if __name__ == "__main__":
    create_pixel_art()
