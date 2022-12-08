from time import process_time_ns

from objects.bdd import BDD, read_bdd
from objects.crossbar import Crossbar, read_crossbar


def parse_command(cmd_str: str):
    return cmd_str.split()


def parse_index(cmd_arr, val_from):
    val = -1
    if len(cmd_arr) > val_from:
        val = int(cmd_arr[val_from])
    return val


def help_cmd():
    print("<required argument> [optional argument]")
    print("read <file> - Reads the file using the format of the given (.bdd or .xbar)")
    print("list <bdd|xbar> - lists the loaded xbars or bdds")
    print("print <bdd|xbar> [item number in list] - Prints the file format to the screen,\n"
          "if no number is given, it will print the most recent loaded object")
    print("tt <bdd|xbar> [item number in list] - Prints the truth table for the most recent\n"
          "xbar or bdd or the object in the numbered list")
    print("verenum <bdd #> <xbar #> - Verify the equivalence of a bdd and xbar via enumeration")
    print("synthesize <filename> [bdd #] - Synthesizes a compact crossbar from a bdd and pushes the result to the top of the list")
    print("save <xbar #> <filename> - Save the xbar to the specified file name")


def list_obj(data: list):
    for i in range(len(data)):
        if type(data[i]) is BDD:
            print(f"[{i}] {data[i].file}")
        elif type(data[i]) is Crossbar:
            print(f"[{i}] {data[i].file}")


if __name__ == "__main__":
    cmd = input(">>> ")
    is_bdd = ["bdd", "bdds"]
    is_xbar = ["xbar", "xbars"]
    bdds = []
    xbars = []
    while cmd != "exit":
        parsed_command = parse_command(cmd.lower())
        if parsed_command[0] == "read":
            if parsed_command[1].split('.')[-1] == "bdd":
                bdds.append(read_bdd(parsed_command[1]))
            elif parsed_command[1].split('.')[-1] =="xbar":
                xbars.append(read_crossbar(parsed_command[1]))
        elif parsed_command[0] == "list":
            if len(parsed_command) < 2:
                print("List document necessary")
                continue
            if parsed_command[1] in is_xbar:
                list_obj(xbars)
            elif parsed_command[1] in is_bdd:
                list_obj(bdds)
        elif parsed_command[0] == "print":
            index = parse_index(parsed_command, 2)
            if parsed_command[1] in is_xbar:
                xbars[index].print_matrix()
            elif parsed_command[1] in is_bdd:
                bdds[index].print()
        elif parsed_command[0] == "tt":
            index = parse_index(parsed_command, 2)
            if parsed_command[1] in is_bdd:
                bdds[index].truth_table()
            elif parsed_command[1] in is_xbar:
                xbars[index].truth_table()
        elif parsed_command[0] == "verenum":
            if len(parsed_command) < 3:
                print("Need a value for the desired bdd and xbar.")
                continue
            index_bdd = int(parsed_command[1])
            index_xbar = int(parsed_command[2])
            start = process_time_ns()
            is_equivalent = bdds[index_bdd].enumeration_verification(xbars[index_xbar])
            end = process_time_ns()
            if len(is_equivalent) == 0:
                print(f"BDD {index_bdd} is equivalent to Crossbar {index_xbar} in {end-start}ns")
            else:
                print(f"BDD {index_bdd} is not equivalent to Crossbar {index_xbar} in {end-start}ns")
        elif parsed_command[0] == "synthesize":
            index = parse_index(parsed_command, 2)
            xbars.append(bdds[index].synthesize_xbar(parsed_command[1]))
        elif parsed_command[0] == "save":
            index = parse_index(parsed_command, 1)
            xbars[index].file = parsed_command[2]
            xbars[index].fprint_matrix()
        else:
            help_cmd()

        cmd = input(">>> ")
