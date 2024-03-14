import io
import json
import logging
import sys

import isa
from isa import Opcode, Instruction


class DataPath:
    data_size: int = None
    data: list = None
    stack_pointer: int = None
    acc: int = None
    rbp: int = None
    user_input_buffer: list[str] = None
    user_output_buffer: list[str] = None

    def __init__(self, data_size: int, input_buffer: list[str], data: list[int], program: list[Instruction]):
        self.data_size = data_size
        self.data = [0] * self.data_size
        self.stack_pointer = self.data_size - 1
        self.acc = 0
        self.rbp = 0
        self.user_input_buffer = input_buffer
        self.user_output_buffer = []

        if data is not None:
            for i in range(len(data)):
                self.data[i] = data[i]
        for i in range(len(program)):
            self.data[i + len(data)] = program[i]

    def latch_stack_pointer(self, sel: Opcode, addr: int = None):
        if sel == Opcode.INC:
            self.stack_pointer += 1
        elif sel == Opcode.DEC:
            self.stack_pointer -= 1
        elif sel == Opcode.MOV:
            self.stack_pointer = addr
        elif sel == Opcode.MOV_RBP:
            self.stack_pointer = self.rbp
        else:
            assert False, "incorrect opcode"

    def latch_rbp(self):
        self.rbp = self.stack_pointer

    # sel_addr = 0 if selecting instruction
    def signal_oe(
        self, sel_addr: bool = False, sel_out: Opcode = None, instruction_addr: int = None, latch_acc: bool = False
    ):
        if not sel_addr:
            res = self.data[instruction_addr]
        else:
            if sel_out == Opcode.OUTPUT:
                res = self.data[self.stack_pointer]

                if (
                    ord("a") <= res <= ord("z")
                    or ord("A") <= res <= ord("Z")
                    or res in {ord(" "), ord("!"), ord(","), ord(".")}
                ):
                    self.user_output_buffer.append(chr(res))
                else:
                    res = str(res)
                    for ch in res:
                        self.user_output_buffer.append(ch)
            else:
                res = self.data[self.stack_pointer]

        if latch_acc is True:
            self.acc = res
        return res

    # sel_addr = 0 if selecting instruction
    def signal_we(self, sel_addr: bool = False, sel_inp: Opcode = None, cu_input: int = None):
        assert sel_addr is True and sel_inp is not None
        if sel_inp == Opcode.INPUT:
            if len(self.user_input_buffer) == 0:
                raise EOFError
            inp = self.user_input_buffer.pop(0)
            self.data[self.stack_pointer] = ord(inp)
        elif sel_inp == Opcode.DUP:
            self.data[self.stack_pointer] = self.acc
        else:
            assert cu_input is not None
            self.data[self.stack_pointer] = cu_input


class ControlUnit:
    program_counter: int = None

    data_path: DataPath = None

    _tick = None

    def __init__(self, data_path: DataPath, starting_addr: int):
        self.program_counter = starting_addr
        self.data_path = data_path
        self._tick = 0

    def tick(self):
        self._tick += 1

    def get_tick(self):
        return self._tick

    # if sel_next == 0 will fetch argument and set it as PC
    def latch_program_counter(self, sel_next: bool):
        if sel_next is True:
            self.program_counter += 1
        else:
            self.program_counter = self.data_path.signal_oe(False, instruction_addr=self.program_counter).arg

    def decode_and_execute_control_flow_instruction(self, instr: Instruction, opcode: Opcode):
        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode is Opcode.JMP:
            addr = instr.arg
            self.program_counter = addr
            self.tick()

            return True

        if opcode is Opcode.JZ:
            addr = instr.arg

            data = self.data_path.signal_oe(True, opcode)
            self.tick()

            if data == 0:
                self.latch_program_counter(sel_next=False)
            else:
                self.latch_program_counter(sel_next=True)
            self.tick()

            return True

        return False

    def decode_and_execute_instruction(self):
        # instr = self.program[self.program_counter]
        instr = self.data_path.signal_oe(False, instruction_addr=self.program_counter)
        opcode = instr.code
        self.tick()

        if self.decode_and_execute_control_flow_instruction(instr, opcode):
            return

        math = {
            Opcode.EQ: lambda a, b: int(a == b),
            Opcode.NEQ: lambda a, b: int(a != b),
            Opcode.ADD: lambda a, b: int(a + b),
            Opcode.SUB: lambda a, b: int(a - b),
            Opcode.MUL: lambda a, b: int(a * b),
            Opcode.DIV: lambda a, b: int(a // b),
            Opcode.MOD: lambda a, b: int(a % b),
        }
        if opcode in math:
            self.data_path.latch_stack_pointer(Opcode.INC)
            self.tick()

            right = self.data_path.signal_oe(True, opcode)
            self.tick()

            self.data_path.latch_stack_pointer(Opcode.INC)
            self.tick()

            left = self.data_path.signal_oe(True, opcode)
            self.tick()

            assert right is not Instruction, opcode

            result = math[opcode](right, left)
            self.tick()

            self.data_path.signal_we(True, opcode, result)

            self.data_path.latch_stack_pointer(Opcode.DEC)
            self.tick()
            self.latch_program_counter(sel_next=True)
            self.tick()

        elif opcode is Opcode.MOV:
            self.data_path.latch_rbp()
            self.tick()

            self.data_path.latch_stack_pointer(opcode, instr.arg)
            self.tick()

            self.latch_program_counter(sel_next=True)
            self.tick()
        elif opcode in {Opcode.INC, Opcode.DEC, Opcode.MOV_RBP}:
            self.data_path.latch_stack_pointer(opcode, instr.arg)
            self.tick()

            self.latch_program_counter(sel_next=True)
            self.tick()

        elif opcode is Opcode.DUP:
            self.data_path.latch_stack_pointer(Opcode.INC)
            self.tick()

            self.data_path.signal_oe(True, opcode, latch_acc=True)
            self.tick()

            self.data_path.latch_stack_pointer(Opcode.DEC)
            self.tick()

            self.data_path.signal_we(True, opcode)
            self.tick()

            self.data_path.latch_stack_pointer(Opcode.DEC)
            self.tick()

            self.latch_program_counter(sel_next=True)
            self.tick()
        elif opcode is Opcode.INPUT:
            self.data_path.signal_we(True, opcode)

            self.data_path.latch_stack_pointer(Opcode.DEC)
            self.latch_program_counter(sel_next=True)
            self.tick()
        elif opcode is Opcode.OUTPUT:
            self.data_path.latch_stack_pointer(Opcode.INC)
            self.data_path.signal_oe(True, opcode)

            self.latch_program_counter(sel_next=True)
            self.tick()
        elif opcode is Opcode.PUSH:
            self.data_path.signal_we(True, opcode, instr.arg)

            self.data_path.latch_stack_pointer(Opcode.DEC)
            self.latch_program_counter(sel_next=True)
            self.tick()

    def __repr__(self):
        """Вернуть строковое представление состояния процессора."""
        state_repr = "TICK: {:3} PC: {:3} SP: {:3} ACC: {}".format(
            self._tick,
            self.program_counter,
            self.data_path.stack_pointer,
            self.data_path.acc,
        )
        return state_repr

        # instr = self.data_path.signal_oe(False, instruction_addr=self.program_counter)
        # opcode = instr.code
        # instr_repr = str(opcode)
        #
        # instr_repr += " {}".format(instr.arg)
        #
        # return "{} \t{}".format(state_repr, instr_repr)


def simulation(code, input_tokens, data_size, limit, data=None):
    data_path = DataPath(data_size, input_tokens, data, code)
    control_unit = ControlUnit(data_path, len(data))
    instr_counter = 0

    logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", control_unit)
    except EOFError:
        logging.warning("Input buffer is empty!")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")
    logging.info("output_buffer: %s", repr("".join(data_path.user_output_buffer)))
    return "".join(data_path.user_output_buffer), instr_counter, control_unit.get_tick()


def run(program_path, input_path):  # entry point
    # print(f"Running with {program_path} {input_path}")
    prog = json.load(open(program_path))
    code = isa.deserialize_instruction_list(prog["program"])
    with open(input_path, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    data = prog.get("data", None)

    output, instr_counter, ticks = simulation(code, input_tokens=input_token, data_size=150, limit=3000, data=data)

    print("".join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


def main(argv):
    if len(argv) != 3:
        print(f"Error in arguments. Expecting: <program_file> <input_file>")
        exit(1)
    run(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
