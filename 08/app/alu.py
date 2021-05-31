from app.constants import *


class Alu:
    ALU_ADD_TO_ASM_COMMAND = '@SP\n'              \
                             'AM=M-1\n'           \
                             'D=M\n'              \
                             'A=A-1\n'            \
                             'M=M+D\n'

    ALU_SUB_TO_ASM_COMMAND = '@SP\n'              \
                             'AM=M-1\n'           \
                             'D=M\n'              \
                             'A=A-1\n'            \
                             'M=M-D\n'

    ALU_NEG_TO_ASM_COMMAND = '@SP\n'              \
                             'A=M-1\n'            \
                             'M=-M\n'

    ALU_BRANCH_TO_ASM_COMMAND = '@SP\n'           \
                                'AM=M-1\n'        \
                                'D=M\n'           \
                                'A=A-1\n'         \
                                'D=M-D\n'         \
                                'M=-1\n'          \
                                '@LABEL{index}\n' \
                                'D;{branch}\n'    \
                                '@SP\n'           \
                                'A=M-1\n'         \
                                'M=0\n'           \
                                '(LABEL{index})\n'

    ALU_AND_TO_ASM_COMMAND = '@SP\n'              \
                             'AM=M-1\n'           \
                             'D=M\n'              \
                             'A=A-1\n'            \
                             'M=D&M\n'

    ALU_OR_TO_ASM_COMMAND = '@SP\n'               \
                            'AM=M-1\n'            \
                            'D=M\n'               \
                            'A=A-1\n'             \
                            'M=D|M\n'

    ALU_NOT_TO_ASM_COMMAND = '@SP\n'              \
                             'A=M-1\n'            \
                             'M=!M\n'

    def __init__(self, args):
        self.vm_command = args[ARG_COMMAND_KEY]
        self.command_index = args[ARG_COMMAND_INDEX_KEY]

    def __alu_add(self):
        return self.ALU_ADD_TO_ASM_COMMAND

    def __alu_sub(self):
        return self.ALU_SUB_TO_ASM_COMMAND

    def __alu_neg(self):
        return self.ALU_NEG_TO_ASM_COMMAND

    def __alu_eq(self):
        return self.ALU_BRANCH_TO_ASM_COMMAND.format(branch=BRANCH_EQ, index=self.command_index)

    def __alu_gt(self):
        return self.ALU_BRANCH_TO_ASM_COMMAND.format(branch=BRANCH_GT, index=self.command_index)

    def __alu_lt(self):
        return self.ALU_BRANCH_TO_ASM_COMMAND.format(branch=BRANCH_LT, index=self.command_index)

    def __alu_and(self):
        return self.ALU_AND_TO_ASM_COMMAND

    def __alu_or(self):
        return self.ALU_OR_TO_ASM_COMMAND

    def __alu_not(self):
        return self.ALU_NOT_TO_ASM_COMMAND

    def translate_to_asm_command(self):
        alu_type_to_asm_handler = {
            'add': self.__alu_add,
            'sub': self.__alu_sub,
            'neg': self.__alu_neg,
            'eq': self.__alu_eq,
            'gt': self.__alu_gt,
            'lt': self.__alu_lt,
            'and': self.__alu_and,
            'or': self.__alu_or,
            'not': self.__alu_not,
        }

        return alu_type_to_asm_handler[self.vm_command]()
