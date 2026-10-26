import os

_instruction_path = os.path.join(os.path.dirname(__file__), "instruction.txt")
try:
    with open(_instruction_path, "r", encoding="utf-8") as _f:
        INSTRUCTION = _f.read()
except Exception:
    INSTRUCTION = ""
