from cs_framework.core.concept import Concept
from pydantic import BaseModel
from typing import Any, Dict


class BattlestartedEvent(BaseModel):
    enemies: list

class BattleendedEvent(BaseModel):
    result: str # WIN/LOSE/ESCAPE
    xp: int

class TurnactionEvent(BaseModel):
    entity: str
    action: str
    target: Any = None

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
        self.waiting_for_ack = False
        self.is_levelup = False
        
        # Battle States: "COMMAND_SELECT", "TARGET_SELECT", "WAITING_ACK"
        self.battle_state = "COMMAND_SELECT" 
        self.command_cursor = 0
        self.target_cursor = 0
        self.selected_action = None # "Attack", "Skill"
        
        # Player Stats Cache
        self.player_stats = {
            "hp": 20, "max_hp": 20, "atk": 5, "def": 2, "spd": 3, "equipment": {}
        }
        self.commands = ["Attack", "Skill", "Escape"]
        self.resources_loaded = False

    def load(self, payload: dict):
        """Action: load"""
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
        """Action: update_player_stats"""
        self.player_stats.update(payload)
        print(f"BattleSystem updated player stats: {self.player_stats}")

    def start_battle(self, payload: dict):
        """Action: start_battle"""
        enemy_names = payload.get("enemies", [])
        self.active_battle = True
        self.log_message = "Battle Start!"
        self.enemies = []
        self.waiting_for_ack = False
        self.is_levelup = False
        self.battle_state = "COMMAND_SELECT"
        self.command_cursor = 0
        self.target_cursor = 0
        self.target_cursor = 0
        
        # Sprites are pre-loaded from enemies.png in gameloop.py
        # No runtime generation needed
        
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
        self.turn_order = ["Player"] + [f"Enemy:{i}" for i in range(len(self.enemies))]
        self.current_turn_index = 0
        self.log_message = f"Enemies: {', '.join([e['name'] for e in self.enemies])}"

    def notify_levelup(self, payload: dict):
        """Action: notify_levelup"""
        self.is_levelup = True
        print("[BattleSystem] Level Up Notification Received")

    def end_battle(self, payload: dict):
        """Action: end_battle"""
        self.active_battle = False
        self.enemies = []
        self.waiting_for_ack = False
        self.is_levelup = False
        
    def get_weapon_target_type(self):
        # Default to SINGLE if no weapon or unknown
        # Check equipped weapon
        equip = self.player_stats.get("equipment", {})
        weapon = equip.get("weapon")
        if weapon:
            return weapon.get("target_type", "SINGLE")
        return "SINGLE"

    def handle_input(self, payload: dict):
        """
        Action: handle_input
        Triggered by InputSystem.BattleCommand
        """
        if not self.active_battle: 
            return

        if self.battle_state == "WAITING_ACK":
            # Any command acknowledges
            print("[BattleSystem] Result Acknowledged")
            self.emit("ResultAcknowledged", {})
            self.waiting_for_ack = False
            self.battle_state = "COMMAND_SELECT"
            return
        
        # Raw key input is better but currently we get command strings or keys via InputSystem?
        # Assuming payload has raw key for Menu navigation if we want fine control
        # Checking InputSystem implementation... usually it maps keys to abstract commands.
        # Let's assume payload might contain "key" if we change input mapping or use "command"
        
        # For now, let's map "UP/DOWN/LEFT/RIGHT/CONFIRM/CANCEL" from payload if available
        # If not, we might need to rely on what InputSystem sends.
        # InputSystem sends "BattleCommand" with "command" = Attack/Skill/Escape/Up/Down/Left/Right/Confirm/Cancel
        
        cmd = payload.get("command")
        print(f"[BattleSystem] ACTION RECEIVED: {cmd}")
        
        if self.battle_state == "COMMAND_SELECT":
            if cmd == "Up":
                self.command_cursor = (self.command_cursor - 1) % len(self.commands)
            elif cmd == "Down":
                self.command_cursor = (self.command_cursor + 1) % len(self.commands)
            elif cmd == "Confirm":
                action = self.commands[self.command_cursor]
                if action == "Escape":
                    self.log_message = "Escaped safely!"
                    self.battle_state = "WAITING_ACK"
                    self.emit("BattleEnded", {"result": "ESCAPE", "xp": 0})
                elif action in ["Attack", "Skill"]:
                    self.selected_action = action
                    # Check Target Type
                    target_type = "SINGLE"
                    if action == "Attack":
                        target_type = self.get_weapon_target_type()
                    elif action == "Skill":
                         # Hardcoded for now, Fireball is ALL
                         target_type = "ALL"
                    
                    if target_type == "SINGLE":
                        self.battle_state = "TARGET_SELECT"
                        self.target_cursor = 0
                        # Ensure cursor is on alive enemy
                        self._fix_target_cursor()
                    else:
                        # ALL target, execute immediately
                        self.emit("TurnAction", {"entity": "Player", "action": action, "target": "ALL"})
            
        elif self.battle_state == "TARGET_SELECT":
            if cmd == "Left":
                self.target_cursor = (self.target_cursor - 1) % len(self.enemies)
                self._fix_target_cursor(-1)
            elif cmd == "Right":
                self.target_cursor = (self.target_cursor + 1) % len(self.enemies)
                self._fix_target_cursor(1)
            elif cmd == "Confirm":
                # Execute on selected target
                target_idx = self.target_cursor
                self.emit("TurnAction", {"entity": "Player", "action": self.selected_action, "target": target_idx})
                self.battle_state = "COMMAND_SELECT" # Reset for next turn (though process_turn might end battle)
            elif cmd == "Cancel":
                self.battle_state = "COMMAND_SELECT"

    def _fix_target_cursor(self, direction=1):
        # Skip dead enemies if we track them (currently we remove dead enemies, so just clamp)
        if not self.enemies: return
        # Since we remove dead enemies from self.enemies immediately in process_turn, 
        # index is always valid for alive enemies.
        pass

    def process_turn(self, payload: dict):
        """
        Action: process_turn
        """
        entity = payload.get("entity")
        action = payload.get("action")
        target_idx = payload.get("target") # Index or "ALL"
        
        print(f"[BattleSystem] Processing turn for {entity}: {action} on {target_idx}")
        
        if entity == "Player":
            damage = 0
            if action == "Attack":
                atk = self.player_stats.get("atk", 10)
                
                targets = []
                if target_idx == "ALL":
                    targets = self.enemies
                elif isinstance(target_idx, int) and 0 <= target_idx < len(self.enemies):
                    targets = [self.enemies[target_idx]]
                else:
                    # Fallback
                    if self.enemies: targets = [self.enemies[0]]

                for target in targets:
                    defence = target.get("def", 0)
                    dmg = max(1, atk - defence // 2)
                    target["hp"] -= int(dmg)
                    # For log just show last hit or summary
                    self.log_message = f"Hit {target['name']} for {int(dmg)} dmg!"

            elif action == "Skill":
                # Fireball AOE logic (already handles all, but let's unify)
                atk = self.player_stats.get("atk", 10)
                damage = max(1, atk * 1.5)
                for e in self.enemies:
                    e["hp"] -= int(damage)
                self.log_message = f"Fireball! {int(damage)} dmg to all!"
        
        # Check deaths
        active_enemies = [e for e in self.enemies if e["hp"] > 0]
        
        if not active_enemies:
            # Win!
            total_xp = sum([e.get("xp_reward", 0) for e in self.enemies]) 
            
            # Keep enemies for rendering until ACK
            self.log_message = f"VICTORY! Gained {total_xp} XP"
            self.waiting_for_ack = True # Wait for ACK
            self.battle_state = "WAITING_ACK"
            self.emit("BattleEnded", {"result": "WIN", "xp": total_xp})
        else:
            self.enemies = active_enemies
            # Enemy Turn (Simple)
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
            pyxel.rect(0, 0, 256, 120, 0) # Black BG Top half
            pyxel.text(100, 10, "BATTLE!", 7)
            
            # Draw Message
            if hasattr(self, "log_message"):
                 pyxel.text(10, 30, self.log_message, 9)
            
            if self.is_levelup:
                 pyxel.text(10, 45, "LEVEL UP!!", 10)
            
            if self.waiting_for_ack:
                 pyxel.text(80, 110, "PRESS ANY KEY TO CONTINUE", pyxel.frame_count % 20 > 10 and 7 or 6)

            # Draw enemies
            for i, enemy in enumerate(self.enemies):
                x = 40 + i*60
                y = 60
                
                # Draw Sprite
                u = enemy.get("sprite_u", 0)
                v = enemy.get("sprite_v", 32)
                bank = enemy.get("sprite_bank", 0)
                pyxel.blt(x, y, bank, u, v, 16, 16, 0)
                
                # Draw Target Cursor
                if self.battle_state == "TARGET_SELECT" and self.target_cursor == i:
                    if pyxel.frame_count % 30 < 15:
                        pyxel.text(x + 5, y - 8, "v", 7) # Flashing cursor
                
                pyxel.text(x, y+18, enemy['name'], 7)
                # HP Bar
                bar_w = 24
                hp_pct = max(0, enemy["hp"]) / enemy["max_hp"]
                pyxel.rect(x, y+26, bar_w, 3, 1) # Red
                pyxel.rect(x, y+26, int(bar_w * hp_pct), 3, 11) # Green
                pyxel.text(x, y+30, f"HP:{max(0, int(enemy['hp']))}", 7)
            
            # Player status
            pyxel.text(10, 100, f"Hero HP: {self.player_stats['hp']}/{self.player_stats['max_hp']}", 7)
            
            # Draw UI (Vertical)
            if self.battle_state in ["COMMAND_SELECT", "TARGET_SELECT"]:
                pyxel.rect(10, 140, 80, 50, 1) # Dark blue menu
                pyxel.rectb(10, 140, 80, 50, 13)
                
                for i, cmd in enumerate(self.commands):
                    color = 7
                    prefix = "  "
                    if i == self.command_cursor and self.battle_state == "COMMAND_SELECT":
                        color = 10
                        prefix = "> "
                    elif self.selected_action == cmd and self.battle_state == "TARGET_SELECT":
                        color = 10 # Highlight selected action while targeting
                        
                    pyxel.text(20, 150 + i*10, f"{prefix}{cmd}", color)
            else:
                # Waiting ACK or other states
                pyxel.rect(10, 180, 236, 20, 1)
                pyxel.text(20, 185, self.log_message, 7)

