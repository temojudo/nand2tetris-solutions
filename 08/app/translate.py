from app.push import *
from app.pop import *
from app.alu import *
from app.branch import *
from app.function import *

from os import listdir
from os.path import isfile

BOOTSTRAP_COMMAND_SP = '@256\n' \
                       'D=A\n'  \
                       '@SP\n'  \
                       'M=D\n'

BOOTSTRAP_COMMAND_SYS_INIT = 'call Sys.init 0'


def get_out_filename(vm_file_or_directory_name):
    path = vm_file_or_directory_name.rstrip('/')

    if isfile(path):
        without_ext = path.split(VM_FILE_EXT)[0]
    else:
        without_ext = path + '/' + path.split('/')[-1]

    return without_ext + ASSEMBLER_FILE_EXT


def remove_comments(commands):
    res = []
    for command in commands:
        parsed_command = command.split('//')[0] if '//' in command else command
        res.append(parsed_command.strip(' '))

    return list(filter(None, res))


def translate_vm_command_to_asm_command(args):
    command_type = args[ARG_COMMAND_KEY].split(' ')[0]
    command_to_class = {
        'push': Push,
        'pop': Pop,
        'label': Branch,
        'goto': Branch,
        'if-goto': Branch,
        'function': Function,
        'call': Function,
        'return': Function,
    }

    command_class = command_to_class.get(command_type, Alu)(args)
    return command_class.translate_to_asm_command()


def translate_vm_commands_to_asm_commands(vm_commands, file, filename):
    current_function_name_as_list = ['']  # I know about this!

    for i, vm_command in enumerate(vm_commands):
        args = {
            ARG_COMMAND_KEY: vm_command,
            ARG_FILENAME_KEY: filename,
            ARG_FUNCTION_NAME_AS_LIST_KEY: current_function_name_as_list,
            ARG_COMMAND_INDEX_KEY: i,
        }
        asm_command = translate_vm_command_to_asm_command(args)
        file.write(asm_command)


def files_contain_sys_vm(filenames):
    for i, filename in enumerate(filenames):
        if START_FILENAME in filename:
            return True
    return False


def parse_folder(folder_name, outfile):
    filenames = [folder_name.rstrip('/') + '/' + filename for filename in listdir(folder_name)
                 if VM_FILE_EXT == filename[-len(VM_FILE_EXT):]]

    if files_contain_sys_vm(filenames):
        outfile.write(BOOTSTRAP_COMMAND_SP)
        translate_vm_commands_to_asm_commands([BOOTSTRAP_COMMAND_SYS_INIT], outfile, '')

    return filenames


def parse_vm_files(vm_file_or_directory_name, out_filename):
    filenames = [vm_file_or_directory_name]
    outfile = open(out_filename, 'w')

    if not isfile(vm_file_or_directory_name):
        filenames = parse_folder(vm_file_or_directory_name, outfile)

    for filename in filenames:
        with open(filename, 'r') as file:
            commands = remove_comments(file.read().split('\n'))
            translate_vm_commands_to_asm_commands(commands, outfile, filename.split('/')[-1])

    outfile.close()


def translate(vm_file_or_directory_name: str) -> None:
    out_filename = get_out_filename(vm_file_or_directory_name)
    parse_vm_files(vm_file_or_directory_name, out_filename)
