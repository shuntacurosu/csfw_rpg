import json
import random
import os

def generate_map():
    width = 64
    height = 64
    
    # 0=Grass, 4=Forest, 5=Desert, 6=Mountain, 7=Village, 2=Water
    tiles = [[0 for _ in range(width)] for _ in range(height)]
    
    # Simple biome generation
    for y in range(height):
        for x in range(width):
            # Noise approximation using sin/cos for smoothish transitions
            import math
            nx = x * 0.1
            ny = y * 0.1
            noise_val = math.sin(nx) + math.cos(ny) + random.random() * 0.5
            
            # Biome logic
            if noise_val > 1.5:
                tiles[y][x] = 4 # Forest
            elif noise_val < -0.5:
                tiles[y][x] = 5 # Desert
            else:
                tiles[y][x] = 0 # Plains
            
            # Mountain barriers
            if noise_val > 2.2:
                tiles[y][x] = 6
                
            # Borders as mountains
            if x == 0 or x == width-1 or y == 0 or y == height-1:
                tiles[y][x] = 6

    # Place Villages (Portals)
    # Village A (Connection to Map 0)
    # Map 0 portal points to Target X=8, Y=8. So let's make 8,8 safe.
    tiles[8][8] = 0
    # Add a visual "Village" entrance nearby?
    # Actually Map 0 portal -> transforms player to 8,8 on Map 1.
    # We want a portal ON Map 1 to go back to Map 0.
    # Let's put a Village tile at 8,3.
    tiles[3][8] = 7 
    
    # Village B (Another safe spot)
    vx, vy = 40, 40
    tiles[vy][vx] = 7
    # Clear area around
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if tiles[vy+j][vx+i] != 7:
                tiles[vy+j][vx+i] = 0

    # Load existing maps (specifically to allow cloning Map 0)
    maps_file = 'assets/data/maps.json'
    with open(maps_file, 'r') as f:
        data = json.load(f)
    
    existing_maps = {m['id']: m for m in data['maps']}
    
    # Create Map 2 (Village B) as a clone of Map 0
    map_village_b = existing_maps.get(0).copy()
    if map_village_b:
        map_village_b["id"] = 2
        map_village_b["name"] = "Village B"
        # Edit portal to point back to Map 1 at correct location
        map_village_b["portals"] = [
             {"x": 10, "y": 15, "target_map": 1, "target_x": 40, "target_y": 41}
        ]
    
    # Update Map 1 (World Map)
    new_map = {
        "id": 1,
        "name": "World Map",
        "width": width,
        "height": height,
        "tiles": tiles,
        "objects": [],
        "portals": [
            # Portal to Village A (Map 0)
            {"x": 8, "y": 3, "target_map": 0, "target_x": 10, "target_y": 14},
            # Portal to Village B (Map 2)
            {"x": 40, "y": 40, "target_map": 2, "target_x": 10, "target_y": 14}
        ],
        "encounter_rate": 0.1
    }
    
    # Reassemble map list
    maps_list = []
    if 0 in existing_maps:
        maps_list.append(existing_maps[0])
    
    maps_list.append(new_map)
    
    if map_village_b:
        maps_list.append(map_village_b)
    
    data['maps'] = maps_list
    
    with open(maps_file, 'w') as f:
        json.dump(data, f, indent=4)
    print("Generated 64x64 World Map with Multiple Villages in maps.json")

if __name__ == "__main__":
    generate_map()
