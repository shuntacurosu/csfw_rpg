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
from concepts.camerasystem import CameraSystem
from concepts.menusystem import MenuSystem
from concepts.shopsystem import ShopSystem
from concepts.effectsystem import EffectSystem

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

            # Define Conditional wrapper once
            class ConditionalSynchronization(Synchronization):
                def __init__(self, name, when, then, cond_fn=None):
                    super().__init__(name, when, then)
                    self.cond_fn = cond_fn
                def execute(self, event):
                    if self.cond_fn and not self.cond_fn(event):
                        return []
                    return super().execute(event)

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
                    
                    # Define mapper factory
                    def make_mapper(static_p):
                        def mapper(event):
                            resolved = {}
                            for k, v in static_p.items():
                                if isinstance(v, str) and v.startswith("event."):
                                    attr = v.split(".", 1)[1]
                                    val = None
                                    if isinstance(event, dict) and attr in event:
                                        val = event[attr]
                                    elif hasattr(event, attr):
                                        val = getattr(event, attr)
                                    elif hasattr(event, "payload") and isinstance(event.payload, dict) and attr in event.payload:
                                        val = event.payload[attr]
                                    resolved[k] = val
                                else:
                                    resolved[k] = v
                            return resolved
                        return mapper

                    # Parse 'then'
                    then_objs = []
                    for action_data in sync_data.get("then", []):
                        target_name = action_data.get("target")
                        target_obj = concepts_map.get(target_name)
                        if not target_obj:
                             print(f"Error: Unknown concept '{target_name}' in rule '{sync_data['name']}'")
                             continue
                        
                        static_payload = action_data.get("payload", {})
                        ai = ActionInvocation(
                            target_concept=target_obj,
                            action_name=action_data["action"],
                            payload_mapper=make_mapper(static_payload)
                        )
                        then_objs.append(ai)
                    
                    # Parse condition
                    condition_str = sync_data.get("condition")
                    if condition_str:
                        class AttrDict:
                            def __init__(self, obj):
                                self._obj = obj
                            def __getattr__(self, name):
                                if isinstance(self._obj, dict) and name in self._obj:
                                    return self._obj[name]
                                if hasattr(self._obj, "payload") and isinstance(self._obj.payload, dict) and name in self._obj.payload:
                                    return self._obj.payload[name]
                                if hasattr(self._obj, name):
                                    return getattr(self._obj, name)
                                return None

                        def get_concept_helper(name):
                            return concepts_map.get(name)

                        def condition_fn(event, runner=runner, condition_str=condition_str):
                            try:
                                ctx = {
                                    "event": AttrDict(event),
                                    "runner": runner,
                                    "concepts": concepts_map,
                                    "get_concept": get_concept_helper
                                }
                                # We allow some basic builtins for string/int operations
                                safe_builtins = {
                                    "len": len,
                                    "int": int,
                                    "str": str,
                                    "list": list,
                                    "dict": dict
                                }
                                return eval(condition_str, {"__builtins__": safe_builtins}, ctx)
                            except Exception as e:
                                # if condition_str:
                                #     print(f"Error evaluating condition '{condition_str}': {e}")
                                return False

                        sync_obj = ConditionalSynchronization(
                            name=sync_data["name"],
                            when=when_obj,
                            then=then_objs,
                            cond_fn=condition_fn
                        )
                    else:
                        sync_obj = Synchronization(
                            name=sync_data["name"],
                            when=when_obj,
                            then=then_objs
                        )
                    
                    runner.register(sync_obj)
                    print(f"Loaded synchronization: {sync_data['name']} (Condition: {condition_str})")
                except Exception as e:
                    print(f"Failed to load rule {sync_data.get('name')}: {e}")
                
    except Exception as e:
        print(f"Error loading rules: {e}")
        # Fallback: try raw dicts if import fails
        if "synchronizations" in locals() and "data" in locals() and "synchronizations" in data:
             runner.synchronizations.extend(data["synchronizations"])

def get_runner():
    # Initialize Runner with RDF Logging
    try:
        from cs_framework.logging.logger import RDFLogger
        logger = None
    except ImportError:
        print("Could not import RDFLogger, logging disabled.")
        logger = None
    runner = Runner(logger=logger)
    
    # Initialize Concepts
    loop = GameLoop("GameLoop")
    input_sys = InputSystem("InputSystem")
    map_sys = MapSystem("MapSystem")
    player = Player("Player")
    npc_sys = NpcSystem("NpcSystem")
    battle_sys = BattleSystem("BattleSystem")
    game_state = GameState("GameState")
    cam_sys = CameraSystem("CameraSystem")
    menu_sys = MenuSystem("MenuSystem")
    shop_sys = ShopSystem("ShopSystem")
    eff_sys = EffectSystem("EffectSystem")
    
    # Register Concepts
    runner.register(loop)
    runner.register(input_sys)
    runner.register(map_sys)
    runner.register(player)
    runner.register(npc_sys)
    runner.register(battle_sys)
    runner.register(game_state)
    runner.register(cam_sys)
    runner.register(menu_sys)
    runner.register(shop_sys)
    runner.register(eff_sys)
    
    # Concept Map for Rule Loading
    concepts_map = {
        "GameLoop": loop,
        "InputSystem": input_sys,
        "MapSystem": map_sys,
        "Player": player,
        "NpcSystem": npc_sys,
        "BattleSystem": battle_sys,
        "GameState": game_state,
        "CameraSystem": cam_sys,
        "MenuSystem": menu_sys,
        "ShopSystem": shop_sys,
        "EffectSystem": eff_sys
    }
    
    # Inject runner into GameLoop so it can drive the loop
    loop.runner = runner
    
    # Set MapSystem reference for NPC collision detection
    npc_sys.set_map_system(map_sys)
    
    # Set NpcSystem reference for player-NPC collision (live positions)
    map_sys.set_npc_system(npc_sys)
    
    # Set Player reference for NPC-to-Player collision avoidance
    npc_sys.set_player(player)

    # Load Rules
    load_rules(runner, "src/sync/rules.yaml", concepts_map)
    
    return runner

def main():
    runner = get_runner()
    
    # Find GameLoop to run it
    # We know the ID or Name. Since we just created it, we can search by name or logic.
    gl = None
    for c in runner.concepts.values():
        if isinstance(c, GameLoop):
            gl = c
            break
            
    if gl:
        # Start Game
        # Triggers GameLoop.init. 
        # This will block until window is closed.
        gl.init({})
        gl.run({})
    else:
        print("GameLoop concept not found.")

if __name__ == "__main__":
    main()
