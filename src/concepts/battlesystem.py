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
        self.enemy_templates = {}
        self.log_message = ""
        self.turn_order = []
        self.current_turn_index = 0
        
        # Player Stats Cache
        self.player_stats = {
            "hp": 20, "max_hp": 20, "atk": 5, "def": 2, "spd": 3
        }

    def load(self, payload: dict):
        """
        Action: load
        """
        import os
        import json
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        enemy_file = os.path.join(base_dir, "assets/data/enemies.json")
        if os.path.exists(enemy_file):
            with open(enemy_file, 'r') as f:
                data = json.load(f)
                self.enemy_templates = {e["name"]: e for e in data.get("enemies", [])}
                print(f"Loaded {len(self.enemy_templates)} enemy types")

    def update_player_stats(self, payload: dict):
        """
        Action: update_player_stats
        """
        self.player_stats.update(payload)
        print(f"BattleSystem updated player stats: {self.player_stats}")

    def start_battle(self, payload: dict):
        """
        Action: start_battle
        """
        enemy_names = payload.get("enemies", [])
        self.active_battle = True
        self.log_message = "Battle Start!"
        self.enemies = []
        
        for name in enemy_names:
            template = self.enemy_templates.get(name)
            if template:
                # Clone and init HP
                enemy = template.copy()
                enemy["hp"] = enemy["max_hp"]
                self.enemies.append(enemy)
            else:
                # Fallback
                self.enemies.append({
                    "name": name, "hp": 10, "max_hp": 10, 
                    "atk": 5, "def": 0, "spd": 2, "xp_reward": 5,
                    "sprite_u": 0, "sprite_v": 32 
                })
        
        # Determine Turn Order (Speed based)
        # For simplicity, Player always goes first for now unless we do initiative roll
        self.turn_order = ["Player"] + [f"Enemy:{i}" for i in range(len(self.enemies))]
        self.current_turn_index = 0
        self.log_message = f"Enemies: {', '.join([e['name'] for e in self.enemies])}"

    def end_battle(self, payload: dict):
        """
        Action: end_battle
        """
        self.active_battle = False
        self.log_message = ""
        
    def handle_input(self, payload: dict):
        """
        Action: handle_input
        Triggered by InputSystem.BattleCommand
        """
        if not self.active_battle: 
            print("[BattleSystem] handle_input IGNORED (not active)")
            return
        
        cmd = payload.get("command") # Attack, Skill, Escape
        print(f"[BattleSystem] ACTION RECEIVED: {cmd}")
        if cmd == "Escape":
            self.active_battle = False
            self.emit("BattleEnded", {"result": "ESCAPE", "xp": 0})
        elif cmd in ["Attack", "Skill"]:
             # Player Action
             self.emit("TurnAction", {"entity": "Player", "action": cmd})

    def process_turn(self, payload: dict):
        """
        Action: process_turn
        """
        entity = payload.get("entity")
        action = payload.get("action")
        print(f"[BattleSystem] Processing turn for {entity}: {action}")
        
        if entity == "Player":
            # Player ATK vs Enemy DEF
            target = self.enemies[0] # Target first for now
            
            damage = 0
            if action == "Attack":
                atk = self.player_stats.get("atk", 10)
                defence = target.get("def", 0)
                damage = max(1, atk - defence // 2)
                target["hp"] -= int(damage)
                self.log_message = f"Hit {target['name']} for {int(damage)} dmg!"
                
            elif action == "Skill":
                # Fireball AOE
                atk = self.player_stats.get("atk", 10) # Magic attack? use atk for now
                damage = max(1, atk * 1.5) # Ignore def
                for e in self.enemies:
                    e["hp"] -= int(damage)
                self.log_message = f"Fireball! {int(damage)} dmg to all!"
        
        # Check deaths
        active_enemies = [e for e in self.enemies if e["hp"] > 0]
        
        if not active_enemies:
            # Win!
            total_xp = sum([e.get("xp_reward", 0) for e in self.enemies]) 
            
            self.enemies = []
            self.log_message = "VICTORY!"
            self.emit("BattleEnded", {"result": "WIN", "xp": total_xp})
        else:
            self.enemies = active_enemies
            # Enemy Turn (Simple)
            # ... Enemy attacks player ...
            # For now just log
            pass
            
    def draw(self, payload: dict):
        """
        Action: draw
        """
        import pyxel
        if self.active_battle:
            # Reset camera MUST happen first
            pyxel.camera(0, 0)
            
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

