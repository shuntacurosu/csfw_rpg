"""
CSFW RPG Sprite Generator
=========================
Generates ALL pixel art sprites for the game.

Layer Structure:
----------------
- Layer1 (Row 0): Ground/Floor tiles - NO transparency
- Layer2 (Row 0-3): Buildings/Objects/Characters - WITH transparency
- Layer3 (Row 6-7): Effects (Reserved for future use)

Image Bank 0 Layout (256x256):
------------------------------
Row 0 (y=0):   Tiles (grass, wall, water, path, forest, desert, mountain, village)
Row 1 (y=16):  Player Character
Row 2 (y=32):  NPCs (Villager, Shopkeeper, etc.)
Row 3 (y=48):  Items & Objects (Chests, Sword, House)

Image Bank 1 Layout (256x256):
------------------------------
Row 0 (y=0):   Enemies (Slime, Bat, Spider, Snake)
Row 1 (y=16):  Enemies (Scorpion, Wolf, Skeleton, Ghost)
"""
from PIL import Image
import random
import os

# Sprite sheet constants
SHEET_WIDTH = 256
SHEET_HEIGHT = 256
TILE_SIZE = 16

# Pyxel Palette (16 colors)
PALETTE = [
    (0, 0, 0),          # 0 Black (transparent key)
    (29, 43, 83),       # 1 Dk Blue
    (126, 37, 83),      # 2 Dk Purple
    (0, 135, 81),       # 3 Dk Green
    (171, 82, 54),      # 4 Brown
    (95, 87, 79),       # 5 Dk Gray
    (194, 195, 199),    # 6 Lt Gray
    (255, 241, 232),    # 7 White
    (255, 0, 77),       # 8 Red
    (255, 163, 0),      # 9 Orange
    (255, 236, 39),     # 10 Yellow
    (0, 228, 54),       # 11 Green
    (41, 173, 255),     # 12 Blue
    (131, 118, 156),    # 13 Indigo
    (255, 119, 168),    # 14 Pink
    (255, 204, 170),    # 15 Peach
]

def create_image_with_palette():
    """Create a new image with Pyxel palette."""
    img = Image.new('P', (SHEET_WIDTH, SHEET_HEIGHT), 0)
    palette_flat = []
    for r, g, b in PALETTE:
        palette_flat.extend([r, g, b])
    palette_flat.extend([0] * (768 - len(palette_flat)))
    img.putpalette(palette_flat)
    return img

def create_main_sprites():
    """Generate Image Bank 0: Tiles, Characters, Items."""
    img = create_image_with_palette()
    pixels = img.load()

    def rect(x, y, w, h, col):
        for j in range(h):
            for i in range(w):
                if 0 <= x+i < SHEET_WIDTH and 0 <= y+j < SHEET_HEIGHT:
                    pixels[x+i, y+j] = col

    def noise(x, y, w, h, base_col, secondary_col, prob=0.1):
        for j in range(h):
            for i in range(w):
                if random.random() < prob:
                    pixels[x+i, y+j] = secondary_col
                else:
                    pixels[x+i, y+j] = base_col

    def line(x1, y1, x2, y2, col):
        """Bresenham's line algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            if 0 <= x1 < SHEET_WIDTH and 0 <= y1 < SHEET_HEIGHT:
                pixels[x1, y1] = col
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def rectb(x, y, w, h, col):
        """Draw rectangle border."""
        for i in range(w):
            if 0 <= x+i < SHEET_WIDTH:
                if 0 <= y < SHEET_HEIGHT:
                    pixels[x+i, y] = col
                if 0 <= y+h-1 < SHEET_HEIGHT:
                    pixels[x+i, y+h-1] = col
        for j in range(h):
            if 0 <= y+j < SHEET_HEIGHT:
                if 0 <= x < SHEET_WIDTH:
                    pixels[x, y+j] = col
                if 0 <= x+w-1 < SHEET_WIDTH:
                    pixels[x+w-1, y+j] = col

    print("=== Generating Image Bank 0 ===")

    # =====================================
    # ROW 0: Tiles (y=0)
    # =====================================
    print("Row 0: Tiles...")
    
    # Tile 0: Grass (0,0)
    noise(0, 0, 16, 16, 11, 3, 0.2)
    pixels[3, 3] = 10
    pixels[12, 8] = 7

    # Tile 1: Wall (16,0)
    rect(16, 0, 16, 16, 6)
    for j in range(0, 16, 4):
        rect(16, j, 16, 1, 5)
    for j in range(0, 16, 4):
        offset = 0 if (j//4) % 2 == 0 else 8
        rect(16+offset+4, j+1, 1, 3, 5)
        rect(16+offset+12, j+1, 1, 3, 5)

    # Tile 2: Water (32,0)
    rect(32, 0, 16, 16, 12)
    pixels[34, 4] = 7
    pixels[35, 4] = 7
    pixels[36, 4] = 7
    pixels[40, 10] = 7
    pixels[41, 10] = 7

    # Tile 3: Path (48,0)
    noise(48, 0, 16, 16, 4, 9, 0.3)

    # Tile 4: Forest (64,0)
    rect(64, 0, 16, 16, 3)
    noise(64, 0, 16, 16, 3, 11, 0.4)
    rect(64+7, 12, 2, 4, 4)

    # Tile 5: Desert (80,0)
    rect(80, 0, 16, 16, 10)
    noise(80, 0, 16, 16, 10, 9, 0.2)

    # Tile 6: Mountain (96,0)
    rect(96, 0, 16, 16, 5)
    for i in range(8):
        rect(96+8-i, 2+i, i*2+1, 14-i, 6)
    rect(96+7, 2, 2, 3, 7)

    # Tile 7: Village Icon (112,0)
    rect(112, 0, 16, 16, 0)
    rect(112+4, 4, 8, 8, 4)
    rect(112+3, 3, 10, 2, 8)

    # =====================================
    # ROW 1: Player (y=16)
    # =====================================
    print("Row 1: Player...")
    
    # Hero (0,16)
    rect(4, 16+4, 8, 10, 8)
    rect(5, 16+2, 6, 4, 15)
    rect(5, 16+2, 6, 2, 4)
    pixels[6, 16+4] = 0
    pixels[9, 16+4] = 0
    rect(5, 16+14, 2, 2, 0)
    rect(9, 16+14, 2, 2, 0)

    # =====================================
    # ROW 2: NPCs (y=32)
    # =====================================
    print("Row 2: NPCs...")
    
    # Villager (0,32)
    rect(4, 32+4, 8, 10, 12)
    rect(5, 32+2, 6, 4, 15)
    rect(5, 32+2, 6, 2, 10)
    pixels[6, 32+4] = 0
    pixels[9, 32+4] = 0
    rect(5, 32+14, 2, 2, 0)
    rect(9, 32+14, 2, 2, 0)

    # Shop Keeper (16,32)
    rect(16+4, 32+4, 8, 10, 10)
    rect(16+5, 32+2, 6, 4, 15)
    rect(16+5, 32+2, 6, 2, 4)
    pixels[16+6, 32+4] = 0
    pixels[16+9, 32+4] = 0
    rect(16+5, 32+14, 2, 2, 0)
    rect(16+9, 32+14, 2, 2, 0)
    pixels[16+11, 32+7] = 9
    pixels[16+12, 32+8] = 9

    # Female Villager (32,32)
    rect(32+4, 32+4, 8, 10, 14)
    rect(32+5, 32+2, 6, 4, 15)
    rect(32+4, 32+2, 8, 2, 4)
    pixels[32+6, 32+4] = 0
    pixels[32+9, 32+4] = 0
    rect(32+5, 32+14, 2, 2, 0)
    rect(32+9, 32+14, 2, 2, 0)

    # Soldier (48,32)
    rect(48+4, 32+4, 8, 10, 1)
    rect(48+5, 32+2, 6, 4, 15)
    rect(48+4, 32+1, 8, 2, 6)
    pixels[48+6, 32+4] = 0
    pixels[48+9, 32+4] = 0
    rect(48+5, 32+14, 2, 2, 1)
    rect(48+9, 32+14, 2, 2, 1)

    # Mage (64,32)
    rect(64+4, 32+4, 8, 10, 2)
    rect(64+5, 32+2, 6, 4, 15)
    rect(64+4, 32+1, 8, 3, 2)
    pixels[64+6, 32+4] = 0
    pixels[64+9, 32+4] = 0
    rect(64+5, 32+14, 2, 2, 0)
    rect(64+9, 32+14, 2, 2, 0)
    pixels[64+12, 32+6] = 4
    pixels[64+12, 32+7] = 4
    pixels[64+12, 32+8] = 4

    # Elder (80,32)
    rect(80+4, 32+4, 8, 10, 7)
    rect(80+5, 32+2, 6, 4, 15)
    rect(80+5, 32+2, 6, 2, 6)
    pixels[80+6, 32+4] = 0
    pixels[80+9, 32+4] = 0
    rect(80+5, 32+14, 2, 2, 0)
    rect(80+9, 32+14, 2, 2, 0)

    # Child (96,32)
    rect(96+5, 32+6, 6, 8, 11)
    rect(96+6, 32+4, 4, 3, 15)
    rect(96+6, 32+4, 4, 1, 4)
    pixels[96+7, 32+5] = 0
    pixels[96+8, 32+5] = 0
    rect(96+6, 32+14, 2, 2, 0)
    rect(96+8, 32+14, 2, 2, 0)

    # Merchant2 (112,32)
    rect(112+4, 32+4, 8, 10, 9)
    rect(112+5, 32+2, 6, 4, 15)
    rect(112+5, 32+2, 6, 2, 5)
    pixels[112+6, 32+4] = 0
    pixels[112+9, 32+4] = 0
    rect(112+5, 32+14, 2, 2, 0)
    rect(112+9, 32+14, 2, 2, 0)

    # =====================================
    # ROW 3: Items & Objects (y=48)
    # =====================================
    print("Row 3: Items & Objects...")
    
    # Chest Closed (0,48)
    rect(0, 48, 16, 16, 0)  # Transparent bg
    rect(2, 48+5, 12, 9, 4)  # Body (Brown)
    rectb(2, 48+5, 12, 9, 1)  # Outline
    rect(1, 48+3, 14, 3, 9)  # Lid (Orange)
    rectb(1, 48+3, 14, 3, 1)  # Lid outline
    pixels[7, 48+9] = 10  # Lock (Yellow)
    pixels[8, 48+9] = 10

    # Chest Opened (16,48)
    rect(16, 48, 16, 16, 0)
    rect(16+2, 48+5, 12, 9, 4)
    rectb(16+2, 48+5, 12, 9, 1)
    rect(16+2, 48+1, 12, 3, 9)  # Open lid
    rectb(16+2, 48+1, 12, 3, 1)
    rect(16+3, 48+6, 10, 7, 1)  # Dark inside

    # Sword (32,48)
    rect(32, 48, 16, 16, 0)
    for i in range(8):
        pixels[32+12-i, 48+4+i] = 7  # Blade (White)
        pixels[32+13-i, 48+5+i] = 13  # Shadow
    line(32+4, 48+12, 32+2, 48+14, 4)  # Hilt
    line(32+8, 48+9, 32+5, 48+12, 10)  # Guard

    # House Exterior / Dungeon Entrance (48,48) -> Tile ID 51
    rect(48, 48, 16, 16, 0)
    # Roof
    line(48+0, 48+6, 48+8, 48+0, 8)
    line(48+15, 48+6, 48+7, 48+0, 8)
    rect(48+1, 48+6, 14, 2, 8)
    rect(48+2, 48+2, 12, 4, 8)
    # Walls (White)
    rect(48+2, 48+8, 12, 8, 7)
    rectb(48+2, 48+8, 12, 8, 1)
    # Door
    rect(48+6, 48+11, 4, 5, 4)
    rectb(48+6, 48+11, 4, 5, 1)

    # Shield (64,48)
    rect(64, 48, 16, 16, 0)
    rect(64+4, 48+2, 8, 12, 12)  # Blue shield
    rectb(64+4, 48+2, 8, 12, 1)
    rect(64+6, 48+4, 4, 8, 7)  # White cross
    rect(64+5, 48+6, 6, 4, 7)

    # Potion (80,48)
    rect(80, 48, 16, 16, 0)
    rect(80+6, 48+3, 4, 3, 6)  # Cork
    rect(80+5, 48+6, 6, 8, 11)  # Green liquid
    rectb(80+5, 48+6, 6, 8, 1)
    pixels[80+6, 48+7] = 7  # Highlight

    print(f"Saved: assets/images/sprites.png")
    return img

def create_enemy_sprites():
    """Generate Image Bank 1: Enemies."""
    img = create_image_with_palette()
    pixels = img.load()
    
    def draw_sprite(u, v, data, color_map):
        """Draw sprite from string pattern."""
        for y, line in enumerate(data):
            for x, char in enumerate(line):
                if x < 16 and y < 16:
                    col = color_map.get(char, 0)
                    if col != 0:
                        pixels[u + x, v + y] = col

    print("=== Generating Image Bank 1 (Enemies) ===")

    # 1. Slime (Blue: 12) u=0, v=0
    slime = [
        "................",
        "................",
        "......XXXX......",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "..XXXXXXXXXXXX..",
        "..X.XX.XX.XX.X..",
        "..X.XX.XX.XX.X..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        "................",
        "................",
        "................",
        "................",
    ]
    draw_sprite(0, 0, slime, {'X': 12, '.': 0})

    # 2. Bat (Purple: 2) u=16, v=0
    bat = [
        "................",
        "X..............X",
        "XX............XX",
        ".XX..........XX.",
        ".XXX........XXX.",
        "..XXX..XX..XXX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        ".....XXXXXX.....",
        "....XX.XX.XX....",
        "....X..XX..X....",
        ".......XX.......",
        "................",
        "................",
        "................",
        "................",
    ]
    draw_sprite(16, 0, bat, {'X': 2, '.': 0})

    # 3. Spider (Gray: 13, Red eyes: 8) u=32, v=0
    spider = [
        "................",
        "................",
        "X..X........X..X",
        ".XX..........XX.",
        "..XX..XXXX..XX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        "...X.RR..RR.X...",
        "..X..RR..RR..X..",
        ".X...XXXXXX...X.",
        "X.....XXXX.....X",
        "......X..X......",
        ".....X....X.....",
        "....X......X....",
        "................",
        "................",
    ]
    draw_sprite(32, 0, spider, {'X': 13, 'R': 8, '.': 0})

    # 4. Snake (Green: 11) u=48, v=0
    snake = [
        "................",
        "................",
        "......XXXX......",
        ".....XXXXXX.....",
        "....XX.XX.XX....",
        "....XXXXXXXX....",
        ".....XXXXXXX....",
        "......XXXX......",
        ".......XX.......",
        ".......XX.......",
        "......XXXX......",
        ".....XXXXXX.....",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "..XXXXXXXXXXXX..",
        "................",
    ]
    draw_sprite(48, 0, snake, {'X': 11, '.': 0})

    # 5. Scorpion (Red: 8) u=0, v=16
    scorpion = [
        "................",
        "X......XX......X",
        "XX....XXXX....XX",
        ".XX..XXXXXX..XX.",
        "..XXXXXXXXXXXX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        "....XXXXXXXX....",
        ".....XXXXXX.....",
        "......XXXX......",
        "......XXXX......",
        ".......XX.......",
        ".......XX.......",
        "...XX..XX..XX...",
        "..XX...XX...XX..",
        "................",
    ]
    draw_sprite(0, 16, scorpion, {'X': 8, '.': 0})

    # 6. Wolf (Gray: 13) u=16, v=16
    wolf = [
        "................",
        ".......X...X....",
        "......XX...XX...",
        ".....XXXXXXXX...",
        "....XXXXXXXXXX..",
        "...XXXXXXXXXXXX.",
        "..XXXXXXXXXXXXX.",
        "..XXX.XXXXX.XXX.",
        "..XXXXXXXXXXXXX.",
        "..XXXXXXXXXXXXX.",
        "...XXXXXXXXXXXX.",
        "....XX.....XX...",
        "....XX.....XX...",
        "....XX.....XX...",
        "................",
        "................",
    ]
    draw_sprite(16, 16, wolf, {'X': 13, '.': 0})

    # 7. Skeleton (White: 7) u=32, v=16
    skeleton = [
        "................",
        "......XXXX......",
        ".....XXXXXX.....",
        ".....X.XX.X.....",
        ".....XXXXXX.....",
        "......XXXX......",
        ".......XX.......",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "...XX..XX..XX...",
        "...XX..XX..XX...",
        ".......XX.......",
        "......XXXX......",
        ".....XX..XX.....",
        ".....XX..XX.....",
        "................",
    ]
    draw_sprite(32, 16, skeleton, {'X': 7, '.': 0})
    
    # 8. Ghost (Lt Gray: 6) u=48, v=16
    ghost = [
        "................",
        "......XXXX......",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "..XXXXXXXXXXXX..",
        "..XX.XX..XX.XX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "...X..X..X..X...",
        "...X..X..X..X...",
        "................",
        "................",
    ]
    draw_sprite(48, 16, ghost, {'X': 6, '.': 0})

    print(f"Saved: assets/images/enemies.png")
    return img

def main():
    """Generate all sprite sheets."""
    os.makedirs("assets/images", exist_ok=True)
    
    # Generate main sprites (Bank 0)
    main_img = create_main_sprites()
    main_img.save("assets/images/sprites.png")
    
    # Generate enemy sprites (Bank 1)
    enemy_img = create_enemy_sprites()
    enemy_img.save("assets/images/enemies.png")
    
    print("\n=== All sprites generated! ===")

if __name__ == "__main__":
    main()
