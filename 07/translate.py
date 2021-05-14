from push import *
from pop import *
from alu import *


def get_out_filename(vm_file_name):
    split_name = vm_file_name.split(VM_FILE_EXT)
    filename = split_name[0].split('/')[-1]
    if split_name:
        return split_name[0] + ASSEMBLER_FILE_EXT, filename
    else:
        raise Exception('Not supported file extension')


def remove_comments(commands):
    res = []
    for command in commands:
        parsed_command = command.split('//')[0] if '//' in command else command
        res.append(parsed_command)

    return list(filter(None, res))


def parse_vm(vm_file):
    file = open(vm_file, 'r')

    commands = file.read().split('\n')
    commands = remove_comments(commands)

    return commands


def translate_vm_command_to_asm_command(vm_command, static_filename, label_index):
    command_type = vm_command.split(' ')[0]
    command_to_class = {
        'push': Push,
        'pop': Pop,
    }

    command_class = command_to_class.get(command_type, Alu)({
        'command': vm_command,
        'filename': static_filename,
        'label_index': label_index
    })
    return command_class.translate_to_asm_command()


def translate_vm_commands_to_asm_commands(vm_commands, out_filename, static_filename):
    file = open(out_filename, 'w')
    for i, vm_command in enumerate(vm_commands):
        asm_command = translate_vm_command_to_asm_command(vm_command, static_filename, i)
        file.write(asm_command)
    file.close()


def translate(vm_file_name: str) -> None:
    vm_commands = parse_vm(vm_file_name)
    out_filename, static_filename = get_out_filename(vm_file_name)
    translate_vm_commands_to_asm_commands(vm_commands, out_filename, static_filename)


if __name__ == '__main__':
    filename = input("Enter vm file path: ")
    translate(filename)
