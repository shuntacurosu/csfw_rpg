import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from cs_framework.engine.runner import Runner
    from cs_framework.core.concept import Concept
    
    class GameState(Concept):
        def __init__(self, name="GameState"):
            super().__init__(name)
            self.current_state = "EXPLORING"

    r = Runner()
    gs = GameState()
    r.register(gs)
    
    concepts_map = {"GameState": gs}
    
    def get_concept_helper(name):
        return concepts_map.get(name)
        
    condition_str = "get_concept('GameState').current_state == 'EXPLORING'"
    
    ctx = {
        "concepts": concepts_map,
        "get_concept": get_concept_helper
    }
    
    result = eval(condition_str, {"__builtins__": {}}, ctx)
    print(f"Eval result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
