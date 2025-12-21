from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class BattlestartedEvent(BaseModel):
    enemies: list

class BattleendedEvent(BaseModel):
    result: str # WIN/LOSE/ESCAPE

class TurnactionEvent(BaseModel):
    entity: str
    action: str

class BattleSystem(Concept):
    """
    Concept: BattleSystem
    Emits Events: BattleStarted, BattleEnded, TurnAction
    """
    __events__ = {
        "BattleStarted": BattlestartedEvent,
        "BattleEnded": BattleendedEvent,
        "TurnAction": TurnactionEvent
    }

    def __init__(self, name: str = "BattleSystem"):
        super().__init__(name)
        self.active_battle = False
        self.enemies = []
        self.turn_order = []
        self.current_turn_index = 0



    def start_battle(self, payload: dict):
        """
        Action: start_battle
        """
        enemy_names = payload.get("enemies", [])
        print(f"Battle started with {enemy_names}")
        self.active_battle = True
        # Initialize enemies with stats
        self.enemies = []
        for name in enemy_names:
            self.enemies.append({
                "name": name,
                "hp": 20,
                "max_hp": 20
            })
        
        self.turn_order = ["Player"] + self.enemies
        self.current_turn_index = 0
        self.log_message = "Battle Start!"

    def end_battle(self, payload: dict):
        """
        Action: end_battle
        """
        print("Battle ended")
        self.active_battle = False
        self.enemies = []
        self.log_message = ""
        
    def handle_input(self, payload: dict):
        """
        Action: handle_input
        Triggered by InputSystem.BattleCommand
        """
        if not self.active_battle: return
        
        idx = payload.get("command_idx")
        
        if idx == 1:
            self.emit("TurnAction", {"entity": "Player", "action": "Attack"})
        elif idx == 2:
            self.emit("TurnAction", {"entity": "Player", "action": "Skill"}) 
        elif idx == 3:
            self.emit("BattleEnded", {"result": "ESCAPE"})

    def process_turn(self, payload: dict):
        """
        Action: process_turn
        """
        entity = payload.get("entity")
        action = payload.get("action")
        
        if entity == "Player":
            if action == "Attack":
                if not self.enemies: return
                target = self.enemies[0]
                damage = 5
                target["hp"] -= damage
                self.log_message = f"Player attacks {target['name']} for {damage} dmg!"
                
            elif action == "Skill":
                damage = 10
                self.log_message = f"Player uses Fireball! All take {damage} dmg!"
                for enemy in self.enemies:
                    enemy["hp"] -= damage
        
        # Check deaths
        self.enemies = [e for e in self.enemies if e["hp"] > 0]
        
        if not self.enemies:
            self.log_message = "VICTORY!"
            # Small delay or immediate end?
            self.emit("BattleEnded", {"result": "WIN"})
            
    def draw(self, payload: dict):
        """
        Action: draw
        """
        import pyxel
        if self.active_battle:
            # Draw battle overlay
            pyxel.rect(0, 0, 256, 256, 0) # Black BG
            pyxel.text(100, 20, "BATTLE START!", 7)
            
            # Draw Message
            if hasattr(self, "log_message"):
                 pyxel.text(10, 40, self.log_message, 9)

            # Draw enemies
            for i, enemy in enumerate(self.enemies):
                x = 50 + i*60
                y = 100
                pyxel.rect(x, y, 16, 16, 8) # Sprite placeholder
                pyxel.text(x, y+20, f"{enemy['name']}", 7)
                # HP Bar
                hp_pct = max(0, enemy["hp"]) / enemy["max_hp"]
                pyxel.rect(x, y+30, 20, 4, 1) # Red bg
                pyxel.rect(x, y+30, int(20 * hp_pct), 4, 11) # Green fg
                pyxel.text(x+22, y+29, f"{enemy['hp']}", 7)
            
            # Draw UI
            pyxel.rect(10, 180, 236, 60, 1) # Dark blue menu
            pyxel.text(20, 190, "1. ATTACK  2. FIREBALL  3. ESCAPE", 7)

