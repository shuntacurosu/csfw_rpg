"""
JSON Refactoring Tool for CSFW RPG
Splits maps.json and npcs.json into smaller, location-based files.
"""
import json
import os

def split_maps():
    """Split maps.json into individual map files."""
    with open('assets/data/maps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    maps = data['maps']
    print(f"Total maps: {len(maps)}")
    
    # Create maps directory
    os.makedirs('assets/data/maps', exist_ok=True)
    
    # Create index
    index = {"maps": []}
    
    for m in maps:
        map_id = m['id']
        map_name = m['name']
        file_name = map_name.lower().replace(' ', '_') + '.json'
        
        index["maps"].append({
            "id": map_id,
            "name": map_name,
            "file": file_name
        })
        
        # Write individual map file
        map_path = f'assets/data/maps/{file_name}'
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(m, f, indent=4)
        print(f"  Created: {map_path}")
    
    # Write index
    with open('assets/data/maps/index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4)
    print("  Created: assets/data/maps/index.json")

def split_npcs():
    """Split npcs.json by map_id."""
    with open('assets/data/npcs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    npcs = data['npcs']
    print(f"Total NPCs: {len(npcs)}")
    
    # Create npcs directory
    os.makedirs('assets/data/npcs', exist_ok=True)
    
    # Group by map_id
    by_map = {}
    for npc in npcs:
        map_id = npc.get('map_id', 0)
        if map_id not in by_map:
            by_map[map_id] = []
        by_map[map_id].append(npc)
    
    # Create index
    index = {"npc_files": []}
    
    for map_id, npc_list in by_map.items():
        file_name = f'map_{map_id}_npcs.json'
        index["npc_files"].append({
            "map_id": map_id,
            "file": file_name
        })
        
        # Write individual NPC file
        npc_path = f'assets/data/npcs/{file_name}'
        with open(npc_path, 'w', encoding='utf-8') as f:
            json.dump({"npcs": npc_list}, f, indent=4)
        print(f"  Created: {npc_path} ({len(npc_list)} NPCs)")
    
    # Write index
    with open('assets/data/npcs/index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4)
    print("  Created: assets/data/npcs/index.json")

if __name__ == "__main__":
    print("=== Splitting maps.json ===")
    split_maps()
    print("\n=== Splitting npcs.json ===")
    split_npcs()
    print("\n=== Done! ===")
