from app.constants import *


class Push:

    PUSH_STATIC_TO_ASM_COMMAND = '@{arg}\n'               \
                                 'D=M\n'                  \
                                 '@SP\n'                  \
                                 'M=M+1\n'                \
                                 'A=M-1\n'                \
                                 'M=D\n'

    PUSH_CONSTANT_TO_ASM_COMMAND = '@{arg}\n'             \
                                   'D=A\n'                \
                                   '@SP\n'                \
                                   'M=M+1\n'              \
                                   'A=M-1\n'              \
                                   'M=D\n'

    PUSH_TEMP_OR_POINTER_TO_ASM_COMMAND = '@{register}\n' \
                                          'D=A\n'         \
                                          '@{arg}\n'      \
                                          'D=D+A\n'       \
                                          'A=D\n'         \
                                          'D=M\n'         \
                                          '@SP\n'         \
                                          'A=M\n'         \
                                          'M=D\n'         \
                                          '@SP\n'         \
                                          'M=M+1\n'

    PUSH_OTHERS_TO_ASM_COMMAND = '@{register}\n'          \
                                 'D=M\n'                  \
                                 '@{arg}\n'               \
                                 'D=D+A\n'                \
                                 'A=D\n'                  \
                                 'D=M\n'                  \
                                 '@SP\n'                  \
                                 'A=M\n'                  \
                                 'M=D\n'                  \
                                 '@SP\n'                  \
                                 'M=M+1\n'

    def __init__(self, args):
        self.command_args = args[ARG_COMMAND_KEY].split(' ')
        self.filename = args[ARG_FILENAME_KEY]

    def __push_local(self):
        return self.PUSH_OTHERS_TO_ASM_COMMAND.format(register=LOCAL_REGISTER, arg=self.command_args[2])

    def __push_argument(self):
        return self.PUSH_OTHERS_TO_ASM_COMMAND.format(register=ARGUMENT_REGISTER, arg=self.command_args[2])

    def __push_this(self):
        return self.PUSH_OTHERS_TO_ASM_COMMAND.format(register=THIS_REGISTER, arg=self.command_args[2])

    def __push_that(self):
        return self.PUSH_OTHERS_TO_ASM_COMMAND.format(register=THAT_REGISTER, arg=self.command_args[2])

    def __push_constant(self):
        return self.PUSH_CONSTANT_TO_ASM_COMMAND.format(arg=self.command_args[2])

    def __push_static(self):
        return self.PUSH_STATIC_TO_ASM_COMMAND.format(arg=self.filename + '.' + self.command_args[2])

    def __push_pointer(self):
        return self.PUSH_TEMP_OR_POINTER_TO_ASM_COMMAND.format(register=POINTER_REGISTER, arg=self.command_args[2])

    def __push_temp(self):
        return self.PUSH_TEMP_OR_POINTER_TO_ASM_COMMAND.format(register=TEMP_REGISTER, arg=self.command_args[2])

    def translate_to_asm_command(self):
        segment_to_asm_handler = {
            'local': self.__push_local,
            'argument': self.__push_argument,
            'this': self.__push_this,
            'that': self.__push_that,
            'constant': self.__push_constant,
            'static': self.__push_static,
            'pointer': self.__push_pointer,
            'temp': self.__push_temp,
        }

        return segment_to_asm_handler[self.command_args[1]]()
