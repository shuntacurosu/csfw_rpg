import sys
import os
import yaml # Need to install pyyaml if not present, but usually std env has it? No, need to check.

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from concepts.gameloop import GameLoop
from concepts.inputsystem import InputSystem
from concepts.mapsystem import MapSystem
from concepts.player import Player
from concepts.npcsystem import NpcSystem
from concepts.battlesystem import BattleSystem
from concepts.gamestate import GameState

try:
    from cs_framework.engine.runner import Runner
except ImportError:
    print("Could not import Runner.")
    sys.exit(1)

def load_rules(runner, rules_file, concepts_map):
    if not os.path.exists(rules_file):
        print(f"Warning: Rules file {rules_file} not found.")
        return

    try:
        with open(rules_file, 'r') as f:
            data = yaml.safe_load(f)
            
        if "synchronizations" in data:
            try:
                from cs_framework.core.synchronization import Synchronization, EventPattern, ActionInvocation
            except ImportError:
                print("Could not import synchronization primitives.")
                return

            for sync_data in data["synchronizations"]:
                try:
                    # Parse 'when'
                    when_data = sync_data["when"]
                    source_name = when_data["source"]
                    source_obj = concepts_map.get(source_name)
                    if not source_obj:
                         print(f"Error: Unknown concept '{source_name}' in rule '{sync_data['name']}'")
                         continue

                    when_obj = EventPattern(
                        source_concept=source_obj,
                        event_name=when_data["event"]
                    )
                    
                    # Parse 'then'
                    then_objs = []
                    for action_data in sync_data["then"]:
                        target_name = action_data["target"]
                        target_obj = concepts_map.get(target_name)
                        if not target_obj:
                             print(f"Error: Unknown concept '{target_name}' in rule '{sync_data['name']}'")
                             continue
                             
                        # ActionInvocation expects: target_concept, action_name, payload_mapper
                        static_payload = action_data.get("payload", {})
                        
                        # Define mapper
                        def make_mapper(p):
                            return lambda event: p
                        
                        ai = ActionInvocation(
                            target_concept=target_obj,
                            action_name=action_data["action"],
                            payload_mapper=make_mapper(static_payload)
                        )
                        then_objs.append(ai)
                    
                    # Create Synchronization
                    sync_obj = Synchronization(
                        name=sync_data["name"],
                        when=when_obj,
                        then=then_objs
                    )
                    
                    runner.register(sync_obj)
                    print(f"Loaded synchronization: {sync_data['name']}")
                except Exception as e:
                    print(f"Failed to load rule {sync_data.get('name')}: {e}")
                
    except Exception as e:
        print(f"Error loading rules: {e}")
        # Fallback: try raw dicts if import fails
        if "synchronizations" in locals() and "data" in locals() and "synchronizations" in data:
             runner.synchronizations.extend(data["synchronizations"])


def main():
    runner = Runner()
    
    # Register Concepts
    # Assuming the concepts are singletons for this runner
    gl = GameLoop()
    inp = InputSystem()
    ms = MapSystem()
    pl = Player()
    npc = NpcSystem()
    btl = BattleSystem()
    gs = GameState()

    runner.register(gl)
    runner.register(inp)
    runner.register(ms)
    runner.register(pl)
    runner.register(npc)
    runner.register(btl)
    runner.register(gs)
    
    # Concept Map for Rule Loading
    concepts_map = {
        "GameLoop": gl,
        "InputSystem": inp,
        "MapSystem": ms,
        "Player": pl,
        "NpcSystem": npc,
        "BattleSystem": btl,
        "GameState": gs
    }
    
    # Inject runner into GameLoop so it can drive the loop
    gl.runner = runner

    # Load Rules
    load_rules(runner, "src/sync/rules.yaml", concepts_map)

    # Start Game
    # Triggers GameLoop.init. 
    # Since we don't have a rule for "Start" -> "GameLoop.init", we call it manually to bootstrap.
    gl.init({})
    
    # Run the Pyxel loop (blocking)
    gl.run({})

if __name__ == "__main__":
    main()
