from PIL import Image, ImageDraw
import os

def create_sprites():
    # Create 256x256 image (Pyxel default bank size)
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Helper to draw a 16x16 tile
    def draw_tile(gx, gy, color, label=None, pattern=None):
        x = gx * 16
        y = gy * 16
        draw.rectangle([x, y, x + 15, y + 15], fill=color)
        
        # Add a simple border
        draw.rectangle([x, y, x + 15, y + 15], outline=(0,0,0,100))
        
        if pattern == 'brick':
            draw.line([x, y+8, x+15, y+8], fill=(0,0,0,100))
            draw.line([x+8, y, x+8, y+8], fill=(0,0,0,100))
        elif pattern == 'water':
            draw.line([x+2, y+4, x+10, y+4], fill=(255,255,255,128))
            draw.line([x+6, y+10, x+14, y+10], fill=(255,255,255,128))
        elif pattern == 'grass':
            draw.point([x+4, y+4], fill=(0,255,0,100))
            draw.point([x+10, y+8], fill=(0,255,0,100))
            draw.point([x+3, y+12], fill=(0,255,0,100))
            
        if label:
            # Simple "face" for characters
            # Eyes
            draw.rectangle([x+4, y+4, x+5, y+5], fill=(0,0,0))
            draw.rectangle([x+10, y+4, x+11, y+5], fill=(0,0,0))
            # Mouth
            draw.rectangle([x+4, y+10, x+11, y+10], fill=(0,0,0))

    # --- Tiles (Row 0) ---
    # 0: Grass
    draw_tile(0, 0, (100, 200, 100), pattern='grass')
    # 1: Wall
    draw_tile(1, 0, (120, 120, 120), pattern='brick')
    # 2: Water
    draw_tile(2, 0, (50, 100, 200), pattern='water')
    # 3: Path
    draw_tile(3, 0, (200, 150, 100))

    # --- Characters (Row 1: Hero at 0,16 -> tile_y=1) ---
    # Hero (Red)
    draw_tile(0, 1, (200, 50, 50), label="Hero")
    
    # --- NPCs (Row 2: Villager at 0,32 -> tile_y=2) ---
    # Villager (Cyan/Blue)
    draw_tile(0, 2, (50, 150, 200), label="Npc")

    # Save
    out_path = "assets/images/sprites.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"Generated clean sprites at {out_path}")

if __name__ == "__main__":
    create_sprites()
