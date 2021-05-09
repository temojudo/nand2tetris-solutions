from constants import *


def get_out_filename(asm_file):
    split_name = asm_file.split(ASSEMBLER_FILE_EXT)
    if split_name:
        return split_name[0] + HACK_FILE_EXT
    else:
        raise Exception('Not supported file extension')


def remove_comments(commands):
    res = []
    for command in commands:
        parsed_command = command.split('//')[0] if '//' in command else command
        res.append(parsed_command)

    return res


def remove_whitespaces(commands):
    without_whitespaces = [''.join(command.split()) for command in commands]
    return list(filter(None, without_whitespaces))


def parse_assembler(asm_file):
    file = open(asm_file, 'r')

    commands = file.read().split('\n')
    commands = remove_comments(commands)
    commands = remove_whitespaces(commands)

    return commands


def resolve_label_values(symbols, commands):
    commands_without_labels = []
    labels_count = 0

    for index, command in enumerate(commands):
        if command[0] == '(' and command[-1] == ')':
            label = command[1: -1]
            symbols[label] = index - labels_count
            labels_count += 1
        else:
            commands_without_labels.append(command)

    return commands_without_labels


def get_symbol_values(commands):
    symbols = COMMON_SYMBOL_DICT.copy()
    commands = resolve_label_values(symbols, commands)
    return symbols, commands


def resolve_atype_instruction(instruction, symbols, variable_index):
    if instruction in symbols:
        value = symbols[instruction]
    elif instruction.isdigit():
        value = int(instruction)
    else:
        value = variable_index
        symbols[instruction] = value
        variable_index += 1

    return '{0:016b}'.format(value), variable_index


def resolve_ctype_instruction(command):
    if ';' in command:
        dest_comp_stmt, jump_stmt = command.split(';', 1)
        jump_str = JUMP_STMT_TO_BINARY_STR[jump_stmt]
    else:
        dest_comp_stmt = command
        jump_str = '000'

    if '=' in dest_comp_stmt:
        dest_stmt, comp_stmt = dest_comp_stmt.split('=', 1)
        dest_str = DEST_STMT_TO_BINARY_STR[dest_stmt]
    else:
        comp_stmt = dest_comp_stmt
        dest_str = '000'

    addr_str = '1' if 'M' in comp_stmt else '0'
    comp_str = COMP_STMT_TO_BINARY_STR[comp_stmt]

    return '111' + addr_str + comp_str + dest_str + jump_str


def translate_command_to_binary(command, symbols, variable_index):
    if command[0] == '@':
        return resolve_atype_instruction(command[1:], symbols, variable_index)
    else:
        return resolve_ctype_instruction(command), variable_index


def translate_commands_to_binary(commands, symbols, out_filename):
    file = open(out_filename, 'w')
    variable_index = VARIABLE_START_INDEX

    for command in commands:
        binary, variable_index = translate_command_to_binary(command, symbols, variable_index)
        file.write(binary + '\n')


def assemble(asm_file: str) -> None:
    commands = parse_assembler(asm_file)
    symbols, commands = get_symbol_values(commands)

    out_filename = get_out_filename(asm_file)
    translate_commands_to_binary(commands, symbols, out_filename)


if __name__ == '__main__':
    filename = input("Enter assembler file path: ")
    assemble(filename)
