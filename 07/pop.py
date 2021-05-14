from constants import *


class Pop:
    POP_STATIC_TO_ASM_COMMAND = '@SP\n'                  \
                                'AM=M-1\n'               \
                                'D=M\n'                  \
                                '@{arg}\n'               \
                                'M=D\n'

    POP_TEMP_OR_POINTER_TO_ASM_COMMAND = '@{register}\n' \
                                         'D=A\n'         \
                                         '@{arg}\n'      \
                                         'D=D+A\n'       \
                                         '@R13\n'        \
                                         'M=D\n'         \
                                         '@SP\n'         \
                                         'AM=M-1\n'      \
                                         'D=M\n'         \
                                         '@R13\n'        \
                                         'A=M\n'         \
                                         'M=D\n'

    POP_OTHERS_TO_ASM_COMMAND = '@{register}\n'          \
                                'D=M\n'                  \
                                '@{arg}\n'               \
                                'D=D+A\n'                \
                                '@R13\n'                 \
                                'M=D\n'                  \
                                '@SP\n'                  \
                                'AM=M-1\n'               \
                                'D=M\n'                  \
                                '@R13\n'                 \
                                'A=M\n'                  \
                                'M=D\n'

    def __init__(self, args):
        self.command_args = args['command'].split(' ')
        self.filename = args['filename']

    def __pop_local(self):
        return self.POP_OTHERS_TO_ASM_COMMAND.format(register=LOCAL_REGISTER, arg=self.command_args[2])

    def __pop_argument(self):
        return self.POP_OTHERS_TO_ASM_COMMAND.format(register=ARGUMENT_REGISTER, arg=self.command_args[2])

    def __pop_this(self):
        return self.POP_OTHERS_TO_ASM_COMMAND.format(register=THIS_REGISTER, arg=self.command_args[2])

    def __pop_that(self):
        return self.POP_OTHERS_TO_ASM_COMMAND.format(register=THAT_REGISTER, arg=self.command_args[2])

    def __pop_static(self):
        return self.POP_STATIC_TO_ASM_COMMAND.format(arg=self.filename + '.' + self.command_args[2])

    def __pop_pointer(self):
        return self.POP_TEMP_OR_POINTER_TO_ASM_COMMAND.format(register=POINTER_REGISTER, arg=self.command_args[2])

    def __pop_temp(self):
        return self.POP_TEMP_OR_POINTER_TO_ASM_COMMAND.format(register=TEMP_REGISTER, arg=self.command_args[2])

    def translate_to_asm_command(self):
        segment_to_asm_handler = {
            'local': self.__pop_local,
            'argument': self.__pop_argument,
            'this': self.__pop_this,
            'that': self.__pop_that,
            'static': self.__pop_static,
            'pointer': self.__pop_pointer,
            'temp': self.__pop_temp,
        }

        return segment_to_asm_handler[self.command_args[1]]()
