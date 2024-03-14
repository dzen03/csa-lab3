import json
import sys
import re

import isa


default_opcodes = [str(oc) for oc in isa.Opcode]

predefined_words = {
    "swap": ["dup", "inc", "-", "dup", "dec", "-", "dup", "inc", "+", "dec"],
    "drop": ["inc"],
    ".s": ["begin", "swap", ".", "1", "swap", "-", "dup", "until"],
}


def str_to_bytes(inp: str):
    return [ord(i) for i in inp]


def remove_funcs(words: list[str], custom_words: dict[str, list[str]], data: list[list[int]]):  # first run
    res: list[str] = []
    ind = 0
    while ind < len(words):
        if words[ind] == ":":
            f_name = words[ind + 1]
            assert f_name not in custom_words and f_name not in default_opcodes, f"word redeclaration: {f_name}"
            ind += 2
            f = []

            while words[ind] != ";":
                f.append(words[ind])
                ind += 1

            custom_words[f_name] = f
        elif words[ind].startswith('."'):
            assert words[ind].endswith('"'), "string is not terminated"

            string_literal = words[ind][2:-1]

            res.append("mov")
            res += remove_funcs(custom_words[".s"], custom_words, data)
            res.append("mov_rbp")
            data.append([0, 0, len(string_literal)] + str_to_bytes(string_literal))
        else:
            if words[ind] in custom_words:
                res += remove_funcs(custom_words[words[ind]], custom_words, data)
            else:
                res.append(words[ind])

        ind += 1
    return res


def calc_mov_addr(data: list[list[int]], data_count):
    return sum([len(data[i]) for i in range(data_count)])


def parse(words: list[str], ind, data: list[list[int]], data_count):  # second run
    prog: list[isa.Instruction] = []
    while ind < len(words):
        if words[ind] == ":":
            assert 1 == 0, "found function declaration on second run"
        elif words[ind] in {"else", "then", "until"}:
            break
        elif words[ind] == "mov":
            prog.append(isa.Instruction("mov", calc_mov_addr(data, data_count[0]) + 1))
            data_count[0] += 1
        elif words[ind] == "mov_rbp":
            prog.append(isa.Instruction("mov_rbp", 0))
        elif words[ind] == "if":
            ind += 1

            parsed, ind = parse(words, ind, data, data_count)  # if body

            prog += [isa.Instruction("inc", 0)]
            prog += [isa.Instruction("jz", len(parsed) + 2)]
            prog += parsed

            assert words[ind] == "else"

            ind += 1  # else word

            parsed, ind = parse(words, ind, data, data_count)  # else body
            prog += [isa.Instruction("jmp", len(parsed) + 1)]
            prog += parsed

            assert words[ind] == "then"
        elif words[ind] == "begin":
            ind += 1

            parsed, ind = parse(words, ind, data, data_count)
            prog += parsed
            prog += [isa.Instruction("inc", 0)]
            prog += [isa.Instruction("jz", 2)]
            prog += [isa.Instruction("jmp", -len(parsed) - 2)]
        else:
            prog.append(isa.Instruction(words[ind], 0))

        ind += 1
    return prog, ind


def calculate_jumps(words: list[isa.Instruction], data_size: int):
    result = words.copy()
    ind = 0
    for i in result:
        if i.code in {isa.Opcode.JMP, isa.Opcode.JZ}:
            i.arg += ind + data_size
        ind += 1

    return result


def translate(input_path, output_path):  # entry point
    # print(f"Translating {input_path} into {output_path}")
    words = open(input_path).read().replace("\n", " ").strip().lower() + " halt"

    words = re.findall(r"((?:\.\".*\")|(?:' ')|(?:\S+))", words)

    custom_words: dict[str, list[str]] = predefined_words
    data = []

    program = remove_funcs(words, custom_words, data)

    data_count = [0]

    program = parse(program, 0, data, data_count)[0]

    data = [j for i in data for j in i]

    program = calculate_jumps(program, len(data))

    serialized_list = isa.serialize_instruction_list(program)

    json.dump({"data": data, "program": serialized_list}, open(output_path, "w"), indent=2)


def main(argv):
    if len(argv) != 3:
        print(f"Error in arguments. Expecting: <input_file> <output_file>")
        exit(1)
    translate(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
