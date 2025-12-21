import pyxel
import os

def run():
    # Invisible window? headless=True is not option in init.
    # Just init minimal.
    pyxel.init(256, 256, title="SpriteGen", capture_scale=1)
    
    # 0,0 Grass (Tile 0)
    pyxel.images[0].rect(0, 0, 16, 16, 11) # Green
    pyxel.images[0].pset(2, 2, 3) # Specks
    pyxel.images[0].pset(10, 10, 3) 
    
    # 16,0 Wall (Tile 1)
    pyxel.images[0].rect(16, 0, 16, 16, 4) # Brown
    pyxel.images[0].rectb(16, 0, 16, 16, 9) # Border orange

    # 32,0 Water (Tile 2)
    pyxel.images[0].rect(32, 0, 16, 16, 12) # Blue
    
    # 48,0 Path (Tile 3)
    pyxel.images[0].rect(48, 0, 16, 16, 13) # Gray/Beige
    pyxel.images[0].pset(50, 2, 7)
    
    # 64,0 Forest (Tile 4)
    pyxel.images[0].rect(64, 0, 16, 16, 3) # Dark Green
    pyxel.images[0].circ(64+8, 0+8, 5, 11) # Tree Top
    
    # 80,0 Desert (Tile 5)
    pyxel.images[0].rect(80, 0, 16, 16, 10) # Yellow
    
    # 96,0 Mountain (Tile 6)
    pyxel.images[0].rect(96, 0, 16, 16, 5) # Dark Gray
    pyxel.images[0].tri(96+8, 0, 96, 0+16, 96+16, 0+16, 13)
    
    # 112,0 Village Icon (Tile 7)
    pyxel.images[0].rect(112, 0, 16, 16, 11) # Grass base
    pyxel.images[0].rect(112+4, 0+8, 8, 8, 4) # House
    pyxel.images[0].tri(112+8, 0, 112+2, 0+8, 112+14, 0+8, 8) # Roof Red

    # 0,16 Hero
    # Clear background for hero usually
    pyxel.images[0].rect(0, 16, 16, 16, 0) # Black/Trans
    pyxel.images[0].rect(0+4, 16+4, 8, 8, 8) # Red Body
    pyxel.images[0].rect(0+4, 16+2, 8, 4, 13) # Head

    # 0,32 Slime
    pyxel.images[0].rect(0, 32, 16, 16, 0)
    pyxel.images[0].circ(0+8, 32+10, 6, 11) # Green Slime

    # Save
    # Cwd is likely repo root or need absolute path logic
    # Assume script is run from repo root
    
    # Ensure assets/images exists
    if not os.path.exists("assets/images"):
        os.makedirs("assets/images")
        
    pyxel.images[0].save("assets/images/sprites.png")
    print("Sprites regenerated and saved to assets/images/sprites.png")
    pyxel.quit()

if __name__ == "__main__":
    run()
