import json
from enum import Enum


class Opcode(Enum):
    EQ = '='
    NEQ = '!='
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    DUP = 'dup'
    OUTPUT = '.'
    INPUT = 'input'

    JMP = 'jmp'
    JZ = 'jz'

    DEC = 'dec'
    INC = 'inc'
    MOV = 'mov'
    MOV_RBP = 'mov_rbp'

    PUSH = 'push'

    HALT = 'halt'

    def __str__(self):
        return self.value

    @staticmethod
    def from_name(name: str):
        return Opcode[name]


class Instruction:
    code: Opcode
    arg: int

    @staticmethod
    def _is_int(n: str):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def __init__(self, code: str, arg: int):
        if self._is_int(code):
            self.code = Opcode.PUSH
            self.arg = int(code)
        elif code.startswith("'") and code.endswith("'"):
            chars = {'\\n': '\n', '\\0': '\0', '\\t': '\t'}

            self.code = Opcode.PUSH
            if code[1] == '\\' and len(code) == 4:
                self.arg = ord(chars[code[1:-1]])
            else:
                self.arg = ord(code[1])
        else:
            self.code = Opcode(code)
            self.arg = arg

    def __str__(self):
        return str(self.serialize())

    def serialize(self):
        return {"code": str(self.code), "arg": self.arg}

    @staticmethod
    def deserialize(data):
        return Instruction(data["code"], data["arg"])


def serialize_instruction_list(instruction_list):
    return [instr.serialize() for instr in instruction_list]


def deserialize_instruction_list(instruction_list):
    return [Instruction.deserialize(instr) for instr in instruction_list]
