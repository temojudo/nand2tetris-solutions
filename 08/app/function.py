from app.constants import *


class Function:
    LABEL_TO_ASM_COMMAND = '({function})\n'

    RETURN_VALUE_TO_ASM_COMMAND = '({function}$ret.{label})\n'

    PUSH_SPACE_FOR_VAR_COMMAND = '@SP\n'                        \
                                 'M=M+1\n'                      \
                                 'A=M-1\n'                      \
                                 'M=0\n'

    PUSH_SPACE_FOR_RETURN_COMMAND = '@{function}$ret.{label}\n' \
                                    'D=A\n'                     \
                                    '@SP\n'                     \
                                    'AM=M+1\n'                  \
                                    'A=A-1\n'                   \
                                    'M=D\n'

    PUSH_SPACE_FOR_SEGMENT_COMMAND = '@{arg}\n'                 \
                                     'D=M\n'                    \
                                     '@SP\n'                    \
                                     'AM=M+1\n'                 \
                                     'A=A-1\n'                  \
                                     'M=D\n'

    MOVE_SP_TO_LCL = '@{args_count}\n'                          \
                     'D=A\n'                                    \
                     '@5\n'                                     \
                     'D=D+A\n'                                  \
                     '@SP\n'                                    \
                     'D=M-D\n'                                  \
                     '@ARG\n'                                   \
                     'M=D\n'                                    \
                     '@SP\n'                                    \
                     'D=M\n'                                    \
                     '@LCL\n'                                   \
                     'M=D\n'

    JUMP_TO_FUNCTION_NAME = '@{function}\n'                     \
                            '0;JMP\n'

    RESOLVE_RETURN_ADDRESS_COMMAND = '@LCL\n'                   \
                                     'D=M\n'                    \
                                     '@R13\n'                   \
                                     'M=D\n'                    \
                                     '@5\n'                     \
                                     'D=A\n'                    \
                                     '@R13\n'                   \
                                     'A=M-D\n'                  \
                                     'D=M\n'                    \
                                     '@R14\n'                   \
                                     'M=D\n'

    RESOLVE_SPACE_FOR_SEGMENT_COMMAND = '@R13\n'                \
                                        'AM=M-1\n'              \
                                        'D=M\n'                 \
                                        '@{register}\n'         \
                                        'M=D\n'

    POP_SPACE_FOR_ARG_COMMAND = '@SP\n'                         \
                                'A=M-1\n'                       \
                                'D=M\n'                         \
                                '@ARG\n'                        \
                                'A=M\n'                         \
                                'M=D\n'                         \
                                '@ARG\n'                        \
                                'D=M+1\n'                       \
                                '@SP\n'                         \
                                'M=D\n'

    JUMP_TO_RETURN_ADDRESS = '@R14\n'                           \
                             'A=M\n'                            \
                             '0;JMP\n'

    def __init__(self, args):
        self.command_args = args[ARG_COMMAND_KEY].split(' ')
        self.filename = args[ARG_FILENAME_KEY]
        self.command_index = args[ARG_COMMAND_INDEX_KEY]

        if len(self.command_args) > 1:
            args[ARG_FUNCTION_NAME_AS_LIST_KEY][0] = self.command_args[1]

    def __function_function(self):
        return self.LABEL_TO_ASM_COMMAND.format(function=self.command_args[1]) + \
               self.PUSH_SPACE_FOR_VAR_COMMAND * int(self.command_args[2])

    def __function_call(self):
        return self.PUSH_SPACE_FOR_RETURN_COMMAND.format(function=self.command_args[1], label=self.command_index) + \
               self.PUSH_SPACE_FOR_SEGMENT_COMMAND.format(arg=LOCAL_REGISTER) +                                     \
               self.PUSH_SPACE_FOR_SEGMENT_COMMAND.format(arg=ARGUMENT_REGISTER) +                                  \
               self.PUSH_SPACE_FOR_SEGMENT_COMMAND.format(arg=THIS_REGISTER) +                                      \
               self.PUSH_SPACE_FOR_SEGMENT_COMMAND.format(arg=THAT_REGISTER) +                                      \
               self.MOVE_SP_TO_LCL.format(args_count=self.command_args[2]) +                                        \
               self.JUMP_TO_FUNCTION_NAME.format(function=self.command_args[1]) +                                   \
               self.RETURN_VALUE_TO_ASM_COMMAND.format(function=self.command_args[1], label=self.command_index)

    def __function_return(self):
        return self.RESOLVE_RETURN_ADDRESS_COMMAND +                                       \
               self.POP_SPACE_FOR_ARG_COMMAND +                                            \
               self.RESOLVE_SPACE_FOR_SEGMENT_COMMAND.format(register=THAT_REGISTER) +     \
               self.RESOLVE_SPACE_FOR_SEGMENT_COMMAND.format(register=THIS_REGISTER) +     \
               self.RESOLVE_SPACE_FOR_SEGMENT_COMMAND.format(register=ARGUMENT_REGISTER) + \
               self.RESOLVE_SPACE_FOR_SEGMENT_COMMAND.format(register=LOCAL_REGISTER) +    \
               self.JUMP_TO_RETURN_ADDRESS

    def translate_to_asm_command(self):
        branch_type_to_asm_handler = {
            'function': self.__function_function,
            'call': self.__function_call,
            'return': self.__function_return,
        }

        return branch_type_to_asm_handler[self.command_args[0]]()
