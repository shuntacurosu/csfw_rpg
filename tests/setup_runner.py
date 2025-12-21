import sys
import os
import types
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mock Pyxel BEFORE importing concepts
mock_pyxel = MagicMock()
# Constants
mock_pyxel.KEY_UP = 0
mock_pyxel.KEY_DOWN = 1
mock_pyxel.KEY_LEFT = 2
mock_pyxel.KEY_RIGHT = 3
mock_pyxel.GAMEPAD1_BUTTON_DPAD_UP = 4
mock_pyxel.GAMEPAD1_BUTTON_DPAD_DOWN = 5
mock_pyxel.GAMEPAD1_BUTTON_DPAD_LEFT = 6
mock_pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT = 7
mock_pyxel.KEY_Z = 8
mock_pyxel.GAMEPAD1_BUTTON_A = 9
mock_pyxel.KEY_X = 10
mock_pyxel.GAMEPAD1_BUTTON_B = 11

# Set btn behavior: Return True only for KEY_RIGHT
def side_effect_btn(key):
    if key == mock_pyxel.KEY_RIGHT:
        return True
    return False

mock_pyxel.btn.side_effect = side_effect_btn
mock_pyxel.btnp.return_value = False

sys.modules["pyxel"] = mock_pyxel

# Now import main which imports concepts
from main import get_runner

# Initialize runner
runner = get_runner()
