"""
CSFW RPG Sprite Generator
=========================
Generates pixel art sprites with clear layer structure:

Layer Structure:
----------------
- Layer1 (Row 0-1): Ground/Floor tiles - NO transparency
- Layer2 (Row 2-3): Buildings/Objects - WITH transparency (colkey=0)
- Layer2 (Row 4-5): Characters (Player, NPCs, Enemies) - WITH transparency
- Layer3 (Row 6-7): Effects (Reserved for future use)

Tile ID Mapping:
----------------
Tile ID | U,V       | Layer | Description
--------|-----------|-------|-------------
0       | 0,0       | L1    | Grass
1       | 16,0      | L2    | Wall (obstacle)
2       | 32,0      | L2    | Water (obstacle)
3       | 48,0      | L1    | Path/Road
4       | 64,0      | L1    | Forest (passable grass with trees aesthetic)
5       | 80,0      | L1    | Desert/Sand
6       | 96,0      | L2    | Mountain (obstacle)
7       | 112,0     | L2    | Village Icon (world map)
51      | 48,48     | L2    | Dungeon Entrance (special portal)

Character sprites are on Row 1-3 (Y=16, 32, 48)
"""
from PIL import Image, ImageDraw
import random
import os

# Sprite sheet constants
SHEET_WIDTH = 256
SHEET_HEIGHT = 256
TILE_SIZE = 16

# Layer definitions (for documentation and future use)
LAYER1_TILES = [0, 3, 4, 5]  # Ground tiles - no transparency
LAYER2_TILES = [1, 2, 6, 7, 51]  # Buildings/obstacles - with transparency

def create_pixel_art():
    """Generate the complete sprite sheet with organized layers."""
    # Create 256x256 image with Palette mode
    img = Image.new('P', (SHEET_WIDTH, SHEET_HEIGHT), 0)
    
    # Pyxel Palette (16 colors)
    palette = [
        0,0,0,          # 0 Black (transparent key)
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
    # Pad to 768 (256 colors * 3 RGB)
    palette.extend([0]*(768-len(palette)))
    img.putpalette(palette)
    
    pixels = img.load()

    # ============================
    # Helper Functions
    # ============================
    def rect(x, y, w, h, col):
        """Draw filled rectangle."""
        for j in range(h):
            for i in range(w):
                if 0 <= x+i < SHEET_WIDTH and 0 <= y+j < SHEET_HEIGHT:
                    pixels[x+i, y+j] = col

    def noise(x, y, w, h, base_col, secondary_col, prob=0.1):
        """Draw noisy rectangle with random secondary color."""
        for j in range(h):
            for i in range(w):
                if random.random() < prob:
                    pixels[x+i, y+j] = secondary_col
                else:
                    pixels[x+i, y+j] = base_col

    # ============================
    # LAYER 1: Ground Tiles (Row 0)
    # These tiles have NO transparency
    # ============================
    print("Generating Layer 1: Ground tiles...")
    
    # Tile 0: Grass (0,0) - Green(11) with Dark Green(3)
    noise(0, 0, 16, 16, 11, 3, 0.2)
    pixels[3,3] = 10  # Yellow flower
    pixels[12,8] = 7  # White flower

    # Tile 3: Path (48,0) - Brown(4) with Orange(9) details
    noise(48, 0, 16, 16, 4, 9, 0.3)

    # Tile 4: Forest (64,0) - Dark Green trees as ground variant
    rect(64, 0, 16, 16, 3)  # Base Dk Green
    noise(64, 0, 16, 16, 3, 11, 0.4)  # Lighter green leaves
    rect(64+7, 12, 2, 4, 4)  # Brown trunk

    # Tile 5: Desert (80,0) - Yellow/Orange sand
    rect(80, 0, 16, 16, 10)  # Yellow base
    noise(80, 0, 16, 16, 10, 9, 0.2)  # Orange specks

    # ============================
    # LAYER 2: Buildings/Obstacles (Row 0 continued)
    # These tiles have transparency (color 0)
    # ============================
    print("Generating Layer 2: Building/Obstacle tiles...")
    
    # Tile 1: Wall (16,0) - Gray bricks
    rect(16, 0, 16, 16, 6)  # Lt Gray base
    for j in range(0, 16, 4):
        rect(16, j, 16, 1, 5)  # Dark horizontal lines
    for j in range(0, 16, 4):
        offset = 0 if (j//4)%2==0 else 8
        rect(16+offset+4, j+1, 1, 3, 5)
        rect(16+offset+12, j+1, 1, 3, 5)
        
    # Tile 2: Water (32,0) - Blue with waves
    rect(32, 0, 16, 16, 12)  # Blue base
    pixels[34, 4] = 7; pixels[35, 4] = 7; pixels[36, 4] = 7  # White waves
    pixels[40, 10] = 7; pixels[41, 10] = 7

    # Tile 6: Mountain (96,0) - Grey peaks (obstacle)
    rect(96, 0, 16, 16, 5)  # Dk Gray base
    for i in range(8):
        rect(96+8-i, 2+i, i*2+1, 14-i, 6)  # Lt Gray mountain shape
    rect(96+7, 2, 2, 3, 7)  # Snowy cap

    # Tile 7: Village Icon (112, 0) - For World Map (transparent bg)
    rect(112, 0, 16, 16, 0)  # Transparent bg
    rect(112+4, 4, 8, 8, 4)  # House body (Brown)
    rect(112+3, 3, 10, 2, 8)  # Red roof

    # Tile 51: Dungeon Entrance (48,48) - Dark cave entrance
    # Note: Located at position (48, 48) to match tile ID 51 calculation
    rect(48, 48, 16, 16, 0)  # Transparent bg
    rect(48+3, 48+3, 10, 10, 5)  # Dark gray frame
    rect(48+4, 48+4, 8, 8, 0)   # Black entrance

    # ============================
    # LAYER 2: Characters (Row 1-3)
    # ============================
    print("Generating Layer 2: Character sprites...")
    
    # --- Row 1: Player Character ---
    # Hero (0,16) - Red armor
    rect(4, 16+4, 8, 10, 8)   # Red Cape/Armor
    rect(5, 16+2, 6, 4, 15)   # Face (Peach)
    rect(5, 16+2, 6, 2, 4)    # Hair (Brown)
    pixels[6, 16+4] = 0       # Left eye
    pixels[9, 16+4] = 0       # Right eye
    rect(5, 16+14, 2, 2, 0)   # Left leg
    rect(9, 16+14, 2, 2, 0)   # Right leg

    # --- Row 2: NPCs ---
    # Villager (0,32) - Blue tunic
    rect(4, 32+4, 8, 10, 12)   # Blue
    rect(5, 32+2, 6, 4, 15)    # Face
    rect(5, 32+2, 6, 2, 10)    # Blonde Hair
    pixels[6, 32+4] = 0
    pixels[9, 32+4] = 0
    rect(5, 32+14, 2, 2, 0)
    rect(9, 32+14, 2, 2, 0)

    # Shop Keeper (16,32) - Yellow apron
    rect(16+4, 32+4, 8, 10, 10)  # Yellow apron
    rect(16+5, 32+2, 6, 4, 15)   # Face
    rect(16+5, 32+2, 6, 2, 4)    # Brown Hair
    pixels[16+6, 32+4] = 0
    pixels[16+9, 32+4] = 0
    rect(16+5, 32+14, 2, 2, 0)
    rect(16+9, 32+14, 2, 2, 0)
    pixels[16+11, 32+7] = 9   # Orange coin
    pixels[16+12, 32+8] = 9

    # Female Villager (32,32) - Pink dress
    rect(32+4, 32+4, 8, 10, 14)
    rect(32+5, 32+2, 6, 4, 15)
    rect(32+4, 32+2, 8, 2, 4)   # Long brown hair
    pixels[32+6, 32+4] = 0
    pixels[32+9, 32+4] = 0
    rect(32+5, 32+14, 2, 2, 0)
    rect(32+9, 32+14, 2, 2, 0)

    # Soldier (48,32) - Dk Blue armor
    rect(48+4, 32+4, 8, 10, 1)
    rect(48+5, 32+2, 6, 4, 15)
    rect(48+4, 32+1, 8, 2, 6)   # Silver helmet
    pixels[48+6, 32+4] = 0
    pixels[48+9, 32+4] = 0
    rect(48+5, 32+14, 2, 2, 1)
    rect(48+9, 32+14, 2, 2, 1)

    # Mage (64,32) - Purple robe
    rect(64+4, 32+4, 8, 10, 2)
    rect(64+5, 32+2, 6, 4, 15)
    rect(64+4, 32+1, 8, 3, 2)   # Hood
    pixels[64+6, 32+4] = 0
    pixels[64+9, 32+4] = 0
    rect(64+5, 32+14, 2, 2, 0)
    rect(64+9, 32+14, 2, 2, 0)
    pixels[64+12, 32+6] = 4    # Staff
    pixels[64+12, 32+7] = 4
    pixels[64+12, 32+8] = 4

    # Elder (80,32) - White robe
    rect(80+4, 32+4, 8, 10, 7)
    rect(80+5, 32+2, 6, 4, 15)
    rect(80+5, 32+2, 6, 2, 6)   # Gray hair
    pixels[80+6, 32+4] = 0
    pixels[80+9, 32+4] = 0
    rect(80+5, 32+14, 2, 2, 0)
    rect(80+9, 32+14, 2, 2, 0)

    # Child (96,32) - Green, smaller
    rect(96+5, 32+6, 6, 8, 11)
    rect(96+6, 32+4, 4, 3, 15)
    rect(96+6, 32+4, 4, 1, 4)
    pixels[96+7, 32+5] = 0
    pixels[96+8, 32+5] = 0
    rect(96+6, 32+14, 2, 2, 0)
    rect(96+8, 32+14, 2, 2, 0)

    # Merchant2 (112,32) - Orange clothes
    rect(112+4, 32+4, 8, 10, 9)
    rect(112+5, 32+2, 6, 4, 15)
    rect(112+5, 32+2, 6, 2, 5)  # Dark gray hair
    pixels[112+6, 32+4] = 0
    pixels[112+9, 32+4] = 0
    rect(112+5, 32+14, 2, 2, 0)
    rect(112+9, 32+14, 2, 2, 0)

    # --- Row 3: Chest ---
    # Treasure Chest (0,48) - Brown chest
    rect(0, 48, 16, 16, 0)      # Transparent bg
    rect(2, 48+6, 12, 8, 4)     # Brown body
    rect(2, 48+4, 12, 4, 9)     # Orange lid
    rect(6, 48+7, 4, 4, 10)     # Yellow lock

    # ============================
    # LAYER 3: Effects (Reserved)
    # ============================
    print("Layer 3: Reserved for future effects...")
    # Row 6-7 are left empty for future particle effects, magic, etc.

    # ============================
    # Save Sprite Sheet
    # ============================
    out_path = "assets/images/sprites.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"\n=== Generated sprite sheet at {out_path} ===")
    print(f"Layer 1 (Ground):    Tiles {LAYER1_TILES}")
    print(f"Layer 2 (Buildings): Tiles {LAYER2_TILES}")
    print(f"Layer 3 (Effects):   Reserved for future use")

# Export tile layer info for use in game code
def get_tile_layer(tile_id):
    """Returns the layer for a given tile ID (1, 2, or 3)."""
    if tile_id in LAYER1_TILES:
        return 1
    elif tile_id in LAYER2_TILES:
        return 2
    else:
        return 2  # Default to layer 2 for characters/objects

if __name__ == "__main__":
    create_pixel_art()
