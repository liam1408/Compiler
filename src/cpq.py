""" CPQ main file ,
    FileHandling  - handles reading and writing from and into files
    Main - the main code that runs the whole compiler calls
"""
import os
import sys
from lexer_cpq import LexerCPQ
from parser_cpq import ParserCPQ,Success

class FileHandling:
    def __init__(self):
        self.filename = ""

    def read_input_file(self, args):
        if len(args) != 2:
            print("Error! Invalid argument count. Usage: python cpq.py <file_name>.ou")
            return None

        input_file = args[1]
        base_name, extension = os.path.splitext(input_file)

        if extension != ".ou" or not base_name:
            print("Error! Invalid file type. Expected .ou file.")
            sys.stderr.write("Liam Meshulam")
            return None

        self.filename = base_name

        try:
            with open(input_file, "r") as file:
                content = file.read().strip()
                if not content:
                    print("Error! Unable to read file.")
                    sys.stderr.write("Liam Meshulam")
                    return None
                return content
        except IOError:
            print(f"Error: Failed to read the file '{input_file}'.")
            return None

    def write_output_file(self, quad_commands):
        if not self.filename:  # Ensure we have a valid filename
            print("Error! Output filename is missing.")
            return

        output_file = f"{self.filename}.qud"
        try:
            with open(output_file, "w") as file:
                file.writelines(f"{cmd}\n" for cmd in quad_commands)
                file.write("Liam Meshulam")
            print(f"Output written to {output_file}")
            sys.stderr.write("Liam Meshulam")
        except IOError:
            print(f"fio: Unable to write to file '{output_file}'.")



if __name__ == '__main__':
    io = FileHandling()
    lexer = LexerCPQ()
    parser = ParserCPQ()

    file = io.read_input_file(sys.argv)
    if file:
        tokens = lexer.tokenize(file)
        ast = parser.parse(tokens)
        if ast is None:
            print("Error! File has illegal syntax or is corrupted. Check above for details.")
            sys.stderr.write("Liam Meshulam")
            sys.exit(1)

        code = ast.gen()

        optimized = []
        removable = set()
        jumps = []

        # finds redundant jumps and track jump instructions
        for idx, line in enumerate(code):
            tokens = line.split()

            if tokens[0] == 'JUMP' and tokens[1] == str(idx + 2):
                removable.add(idx)
            elif tokens[0] in {'JMPZ', 'JUMP'}:
                jumps.append(idx)

            optimized.append(tokens)

        # adjust jump targets if necessary
        for removed_idx in sorted(removable, reverse=True):
            for jump_idx in jumps:
                target = int(optimized[jump_idx][1])
                if target > removed_idx:
                    optimized[jump_idx][1] = str(target - 1)

        # remove redundant lines
        optimized = [tokens for i, tokens in enumerate(optimized) if i not in removable]

        res =  [' '.join(line) for line in optimized]
        if Success.found_errors == 0:
            io.write_output_file(res)
        else:
            print("syntax errors found aborting creation of .qud file")
