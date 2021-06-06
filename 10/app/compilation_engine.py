from typing import TextIO

from app.constants import XML_LINE_TAB
from app.tokenizer import Tokenizer, TokenType, StatementType


def write_line(line: str, tab_count: int, file: TextIO) -> None:
    file.write(f'{XML_LINE_TAB * tab_count}{line}\n')


class CompilationEngine:

    def __init__(self, tokenizer: Tokenizer, out_file_name: str):
        self.tokenizer = tokenizer
        self.out_file_name = out_file_name

    def write_file(self):
        with open(self.out_file_name, 'w') as file:
            self.compile_class(file)

    def write_token_and_move_next(self, line: str, tab_count: int, file: TextIO):
        write_line(line, tab_count, file)
        self.tokenizer.advance()

    def compile_class(self, file: TextIO) -> None:
        write_line('<class>', 0, file)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), 1, file)
        self.write_token_and_move_next(self.tokenizer.identifier_xml(), 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), 1, file)

        while self.tokenizer.is_token_class_var():
            self.compile_class_var_dec(1, file)

        while self.tokenizer.is_token_callable():
            self.compile_subroutine_dec(1, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), 1, file)
        write_line('</class>', 0, file)

    def compile_class_var_dec(self, tab_count: int, file: TextIO) -> None:
        write_line('<classVarDec>', tab_count, file)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
        self.compile_variable(tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        write_line('</classVarDec>', tab_count, file)

    def compile_subroutine_dec(self, tab_count: int, file: TextIO) -> None:
        write_line('<subroutineDec>', tab_count, file)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)

        if self.tokenizer.is_token_void():
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
        else:
            self.compile_type(tab_count + 1, file)

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        self.compile_parameter_list(tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        self.compile_subroutine_body(tab_count + 1, file)
        write_line('</subroutineDec>', tab_count, file)

    def compile_parameter_list(self, tab_count: int, file: TextIO) -> None:
        write_line('<parameterList>', tab_count, file)

        while not self.tokenizer.is_token_close_parentheses():
            self.compile_type(tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1, file)
            if self.tokenizer.is_token_comma():
                self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        write_line('</parameterList>', tab_count, file)

    def compile_variable(self, tab_count, file: TextIO) -> None:  # doesnt include 'var'
        self.compile_type(tab_count, file)

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count, file)
        while self.tokenizer.is_token_comma():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count, file)

    def compile_type(self, tab_count: int, file: TextIO) -> None:
        if self.tokenizer.token_type() == TokenType.KEYWORD:
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count, file)
        else:
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count, file)

    def compile_subroutine_body(self, tab_count: int, file: TextIO) -> None:
        write_line('<subroutineBody>', tab_count, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        while self.tokenizer.is_token_var():
            self.compile_var_dec(tab_count + 1, file)

        self.compile_statements(tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        write_line('</subroutineBody>', tab_count, file)

    def compile_var_dec(self, tab_count: int, file: TextIO) -> None:
        write_line('<varDec>', tab_count, file)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
        self.compile_variable(tab_count + 1, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        write_line('</varDec>', tab_count, file)

    def compile_statements(self, tab_count: int, file: TextIO) -> None:
        write_line('<statements>', tab_count, file)

        switcher = {
            StatementType.LET: self.compile_let,
            StatementType.IF: self.compile_if,
            StatementType.WHILE: self.compile_while,
            StatementType.DO: self.compile_do,
            StatementType.RETURN: self.compile_return,
        }

        while self.tokenizer.statement() != StatementType.NOT_STATEMENT:
            switcher[self.tokenizer.statement()](tab_count + 1, file)

        write_line('</statements>', tab_count, file)

    def compile_let(self, tab_count: int, file: TextIO) -> None:
        write_line('<letStatement>', tab_count, file)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1, file)

        if self.tokenizer.is_token_open_brackets():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
            self.compile_expression(tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        self.compile_expression(tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        write_line('</letStatement>', tab_count, file)

    def compile_if_while_common(self, tab_count: int, file: TextIO) -> None:
        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)
        self.compile_expression(tab_count, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)
        self.compile_statements(tab_count, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)

    def compile_if(self, tab_count: int, file: TextIO) -> None:
        write_line('<ifStatement>', tab_count, file)

        self.compile_if_while_common(tab_count + 1, file)

        if self.tokenizer.is_token_else():
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
            self.compile_statements(tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        write_line('</ifStatement>', tab_count, file)

    def compile_while(self, tab_count: int, file: TextIO) -> None:
        write_line('<whileStatement>', tab_count, file)
        self.compile_if_while_common(tab_count + 1, file)
        write_line('</whileStatement>', tab_count, file)

    def compile_do(self, tab_count: int, file: TextIO) -> None:
        write_line('<doStatement>', tab_count, file)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
        self.compile_subroutine_call(tab_count + 1, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)

        write_line('</doStatement>', tab_count, file)

    def compile_return(self, tab_count: int, file: TextIO) -> None:
        write_line('<returnStatement>', tab_count, file)
        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)

        if not self.tokenizer.is_token_semicolon():
            self.compile_expression(tab_count + 1, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        write_line('</returnStatement>', tab_count, file)

    def compile_expression(self, tab_count: int, file: TextIO) -> None:
        write_line('<expression>', tab_count, file)
        self.compile_term(tab_count + 1, file)

        while self.tokenizer.is_token_operation():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
            self.compile_term(tab_count + 1, file)

        write_line('</expression>', tab_count, file)

    def compile_term(self, tab_count: int, file: TextIO) -> None:
        write_line('<term>', tab_count, file)

        token_type = self.tokenizer.token_type()
        if token_type == TokenType.INT_CONST:
            self.write_token_and_move_next(self.tokenizer.int_val_xml(), tab_count + 1, file)
        elif token_type == TokenType.STRING_CONST:
            self.write_token_and_move_next(self.tokenizer.string_val_xml(), tab_count + 1, file)
        elif token_type == TokenType.KEYWORD:
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1, file)
        elif self.tokenizer.is_token_open_parentheses():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
            self.compile_expression(tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        elif self.tokenizer.is_token_unary_operation():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
            self.compile_term(tab_count + 1, file)
        elif self.tokenizer.is_next_token_open_brackets():
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
            self.compile_expression(tab_count + 1, file)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
        elif self.tokenizer.is_next_token_open_parentheses_or_dot():
            self.compile_subroutine_call(tab_count + 1, file)
        else:
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1, file)

        write_line('</term>', tab_count, file)

    def compile_subroutine_call(self, tab_count: int, file: TextIO) -> None:
        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count, file)

        if not self.tokenizer.is_token_open_parentheses():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count, file)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)
        self.compile_expression_list(tab_count, file)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count, file)

    def compile_expression_list(self, tab_count: int, file: TextIO) -> None:
        write_line('<expressionList>', tab_count, file)

        if not self.tokenizer.is_token_close_parentheses():
            self.compile_expression(tab_count + 1, file)
            while self.tokenizer.is_token_comma():
                self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1, file)
                self.compile_expression(tab_count + 1, file)

        write_line('</expressionList>', tab_count, file)
