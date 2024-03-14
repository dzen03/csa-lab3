import translator
import emulator

import sys


if __name__ == "__main__":

    def error():
        print(
            "Error in arguments. Usage: python main.py translate {input_file} {output_file}\n"
            "or \n"
            "python main.py run {input_file}"
        )
        exit(1)

    argv = sys.argv
    if len(argv) < 2:
        error()
    mode = argv[1]
    if mode == "translate":
        translator.main(argv[1:])
    elif mode == "run":
        emulator.main(argv[1:])
    else:
        error()
