from PIL import Image
import numpy as np

def apply_pyxel_palette(input_path, output_path):
    # Pyxel default palette (hex)
    pyxel_colors_hex = [
        "000000", "2B335F", "7E2072", "19959C", 
        "8B4852", "395C98", "A9C1FF", "EEEEEE", 
        "D4186C", "D38441", "E9C35B", "70C6A9", 
        "7696DE", "A3A3A3", "FF9798", "EDC7B0"
    ]
    
    # Convert to RGB tuples
    palette_rgb = []
    for hex_color in pyxel_colors_hex:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        palette_rgb.extend((r, g, b))

    # Pad palette to 768 entries (256 colors * 3)
    while len(palette_rgb) < 768:
        palette_rgb.extend((0, 0, 0))

    # Create palette image
    p_img = Image.new('P', (1, 1))
    p_img.putpalette(palette_rgb)

    # Open target image
    try:
        img = Image.open(input_path).convert("RGB")
        
        # Quantize to the palette
        # method=0 (MEDIANCUT), 1 (MAXCOVERAGE), 2 (FASTOCTREE), 3 (LIBIMAGEQUANT)
        # dither=0 (NONE), 1 (FLOYDSTEINBERG)
        # We start with dither=0 for cleanest look
        out = img.quantize(palette=p_img, dither=0)
        
        # Save
        out.save(output_path)
        print(f"Saved quantized image to {output_path}")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    # Input is the high-quality generated file (resized or original if accessible)
    # Using the one in assets/images/sprites.png which was resized
    apply_pyxel_palette("assets/images/sprites.png", "assets/images/sprites.png")
