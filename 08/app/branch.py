from app.constants import *


class Branch:
    BRANCH_LABEL_TO_ASM_COMMAND = '({function}${label})\n'

    BRANCH_IF_GOTO_TO_ASM_COMMAND = '@SP\n'                 \
                                    'AM=M-1\n'              \
                                    'D=M\n'                 \
                                    '@{function}${label}\n' \
                                    'D;JNE\n'

    BRANCH_GOTO_TO_ASM_COMMAND = '@{function}${label}\n'    \
                                 '0;JMP\n'

    def __init__(self, args):
        self.command_args = args[ARG_COMMAND_KEY].split(' ')
        self.filename = args[ARG_FILENAME_KEY]
        self.function_name = args[ARG_FUNCTION_NAME_AS_LIST_KEY][0]

    def __branch_label(self):
        return self.BRANCH_LABEL_TO_ASM_COMMAND.format(function=self.function_name, label=self.command_args[1])

    def __branch_goto(self):
        return self.BRANCH_GOTO_TO_ASM_COMMAND.format(function=self.function_name, label=self.command_args[1])

    def __branch_if_goto(self):
        return self.BRANCH_IF_GOTO_TO_ASM_COMMAND.format(function=self.function_name, label=self.command_args[1])

    def translate_to_asm_command(self):
        branch_type_to_asm_handler = {
            'label': self.__branch_label,
            'goto': self.__branch_goto,
            'if-goto': self.__branch_if_goto,
        }

        return branch_type_to_asm_handler[self.command_args[0]]()
