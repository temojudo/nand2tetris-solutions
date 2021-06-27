from app.constants import XML_LINE_TAB, WHILE_LABEL_BEGIN, WHILE_LABEL_END, ELSE_LABEL_BEGIN, IF_ELSE_LABEL_END, IF_LABEL_BEGIN
from app.symbol_table import SymbolTable
from app.tokenizer import Tokenizer, TokenType, StatementType
from app.vm_writer import VMWriter


class CompilationEngine:

    def __init__(self, tokenizer: Tokenizer, xml_out_file_name: str, vm_out_file_name: str):
        self.tokenizer = tokenizer
        self.out_file_name = xml_out_file_name

        self.class_name = ''
        self.return_type = ''

        self.vm_writer = VMWriter(vm_out_file_name)
        self.xml_file = open(xml_out_file_name, 'w')

        self.symbol_table = SymbolTable()

    def write_file(self) -> None:
        self.compile_class()
        self.close_file()

    def close_file(self) -> None:
        self.xml_file.close()
        self.vm_writer.close_file()

    def write_line(self, line: str, tab_count: int) -> None:
        self.xml_file.write(f'{XML_LINE_TAB * tab_count}{line}\n')

    def write_token_and_move_next(self, line: str, tab_count: int):
        self.write_line(line, tab_count)
        self.tokenizer.advance()

    def compile_class(self) -> None:
        self.write_line('<class>', 0)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), 1)
        self.class_name = self.tokenizer.get_current_token()

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), 1)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), 1)

        while self.tokenizer.is_token_class_var():
            self.compile_class_var_dec(1)

        while self.tokenizer.is_token_callable():
            self.compile_subroutine_dec(1)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), 1)
        self.write_line('</class>', 0)

    def compile_class_var_dec(self, tab_count: int) -> None:
        self.write_line('<classVarDec>', tab_count)

        kind = self.tokenizer.get_current_token()

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        self.compile_variable(kind, tab_count + 1)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_line('</classVarDec>', tab_count)

    def compile_subroutine_dec(self, tab_count: int) -> None:
        self.write_line('<subroutineDec>', tab_count)

        self.symbol_table.start_subroutine()

        function_type = self.tokenizer.get_current_token()
        if function_type == 'method':
            self.symbol_table.define('this', self.class_name, 'argument')

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)  # function | method | constructor

        self.return_type = self.tokenizer.get_current_token()
        if self.tokenizer.is_token_void():  # type
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        else:
            self.compile_type(tab_count + 1)

        function_name = self.tokenizer.get_current_token()

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)  # name
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.compile_parameter_list(tab_count + 1)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.compile_subroutine_body(function_name, function_type, tab_count + 1)
        self.write_line('</subroutineDec>', tab_count)

    def compile_parameter_list(self, tab_count: int) -> int:
        self.write_line('<parameterList>', tab_count)
        count = 0

        while not self.tokenizer.is_token_close_parentheses():
            count += 1
            typ = self.compile_type(tab_count + 1)
            name = self.tokenizer.get_current_token()
            self.symbol_table.define(name, typ, 'argument')
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)
            if self.tokenizer.is_token_comma():
                self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_line('</parameterList>', tab_count)
        return count

    def compile_variable(self, kind: str, tab_count) -> int:  # doesnt include 'var'
        var_type = self.tokenizer.get_current_token()
        self.compile_type(tab_count)

        num_vars = 1

        self.symbol_table.define(self.tokenizer.get_current_token(), var_type, kind)
        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count)

        while self.tokenizer.is_token_comma():
            num_vars += 1
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

            self.symbol_table.define(self.tokenizer.get_current_token(), var_type, kind)
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count)

        return num_vars

    def compile_type(self, tab_count: int) -> str:
        typ = self.tokenizer.get_current_token()
        if self.tokenizer.token_type() == TokenType.KEYWORD:
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count)
        else:
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count)
        return typ

    def compile_subroutine_body(self, function_name: str, function_type: str, tab_count: int) -> None:
        self.write_line('<subroutineBody>', tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        num_vars = 0
        while self.tokenizer.is_token_var():
            num_vars += self.compile_var_dec(tab_count + 1)

        self.vm_writer.write_function(self.class_name, function_name, num_vars)

        if function_type == 'method':
            self.vm_writer.write_method_header()

        if function_type == 'constructor':
            self.vm_writer.write_constructor_header(self.symbol_table.get_num_fields())

        self.compile_statements(tab_count + 1)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.write_line('</subroutineBody>', tab_count)

    def compile_var_dec(self, tab_count: int) -> int:
        self.write_line('<varDec>', tab_count)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        num_vars = self.compile_variable('local', tab_count + 1)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.write_line('</varDec>', tab_count)

        return num_vars

    def compile_statements(self, tab_count: int) -> None:
        self.write_line('<statements>', tab_count)

        switcher = {
            StatementType.LET: self.compile_let,
            StatementType.IF: self.compile_if,
            StatementType.WHILE: self.compile_while,
            StatementType.DO: self.compile_do,
            StatementType.RETURN: self.compile_return,
        }

        while self.tokenizer.statement() != StatementType.NOT_STATEMENT:
            switcher[self.tokenizer.statement()](tab_count + 1)

        self.write_line('</statements>', tab_count)

    def compile_let(self, tab_count: int) -> None:
        self.write_line('<letStatement>', tab_count)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)

        index = self.symbol_table.index_of(self.tokenizer.get_current_token())
        kind = self.symbol_table.kind_of(self.tokenizer.get_current_token())

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)

        is_open_brackets = self.tokenizer.is_token_open_brackets()
        if is_open_brackets:
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_expression(tab_count + 1)

            self.vm_writer.write_push(kind, index)
            self.vm_writer.write_alu('+')

            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.compile_expression(tab_count + 1)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        if is_open_brackets:
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        else:
            self.vm_writer.write_pop('this' if kind == 'field' else kind, index)

        self.write_line('</letStatement>', tab_count)

    def compile_if(self, tab_count: int) -> None:
        self.write_line('<ifStatement>', tab_count)

        label_index = self.symbol_table.next_if_label_index()

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_expression(tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_writer.write_if_goto(IF_LABEL_BEGIN, label_index)
        self.vm_writer.write_goto(ELSE_LABEL_BEGIN, label_index)
        self.vm_writer.write_label(IF_LABEL_BEGIN, label_index)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_statements(tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_writer.write_goto(IF_ELSE_LABEL_END, label_index)
        self.vm_writer.write_label(ELSE_LABEL_BEGIN, label_index)

        if self.tokenizer.is_token_else():
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_statements(tab_count + 1)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.vm_writer.write_label(IF_ELSE_LABEL_END, label_index)
        self.write_line('</ifStatement>', tab_count)

    def compile_while(self, tab_count: int) -> None:
        self.write_line('<whileStatement>', tab_count)

        label_index = self.symbol_table.next_while_label_index()
        self.vm_writer.write_label(WHILE_LABEL_BEGIN, label_index)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_expression(tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_writer.write_alu('not')
        self.vm_writer.write_if_goto(WHILE_LABEL_END, label_index)

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_statements(tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_writer.write_goto(WHILE_LABEL_BEGIN, label_index)
        self.vm_writer.write_label(WHILE_LABEL_END, label_index)

        self.write_line('</whileStatement>', tab_count)

    def compile_do(self, tab_count: int) -> None:
        self.write_line('<doStatement>', tab_count)

        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        self.compile_subroutine_call(tab_count + 1)
        self.vm_writer.write_pop('temp', 0)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_line('</doStatement>', tab_count)

    def compile_return(self, tab_count: int) -> None:
        self.write_line('<returnStatement>', tab_count)
        self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)

        if not self.tokenizer.is_token_semicolon():
            self.compile_expression(tab_count + 1)

        if self.return_type == 'void':
            self.vm_writer.write_push('constant', 0)
        self.vm_writer.write_return()

        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.write_line('</returnStatement>', tab_count)

    def compile_expression(self, tab_count: int) -> None:
        self.write_line('<expression>', tab_count)
        self.compile_term(tab_count + 1)

        while self.tokenizer.is_token_operation():
            op = self.tokenizer.get_current_token()

            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_term(tab_count + 1)

            self.vm_writer.write_alu(op)

        self.write_line('</expression>', tab_count)

    def handle_array_term(self, current_token: str, tab_count: int):
        kind = self.symbol_table.kind_of(current_token)
        index = self.symbol_table.index_of(current_token)
        self.vm_writer.write_push(kind, index)

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_expression(tab_count)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_writer.write_alu('+')
        self.vm_writer.write_pop('pointer', 1)
        self.vm_writer.write_push('that', 0)

    def compile_term(self, tab_count: int) -> None:
        self.write_line('<term>', tab_count)

        token_type = self.tokenizer.token_type()
        current_token = self.tokenizer.get_current_token()

        if token_type == TokenType.INT_CONST:
            self.vm_writer.write_push('constant', self.tokenizer.int_val())
            self.write_token_and_move_next(self.tokenizer.int_val_xml(), tab_count + 1)
        elif token_type == TokenType.STRING_CONST:
            self.vm_writer.write_string(self.tokenizer.string_val())
            self.write_token_and_move_next(self.tokenizer.string_val_xml(), tab_count + 1)
        elif token_type == TokenType.KEYWORD:
            self.vm_writer.write_keyword(current_token)
            self.write_token_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        elif self.tokenizer.is_token_open_parentheses():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_expression(tab_count + 1)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        elif self.tokenizer.is_token_unary_operation():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_term(tab_count + 1)
            self.vm_writer.write_alu('neg' if current_token == '-' else 'not')
        elif self.tokenizer.is_next_token_open_brackets():
            self.handle_array_term(current_token, tab_count + 1)
        elif self.tokenizer.is_next_token_open_parentheses_or_dot():
            self.compile_subroutine_call(tab_count + 1)
        else:
            kind = self.symbol_table.kind_of(current_token)
            index = self.symbol_table.index_of(current_token)
            self.vm_writer.write_push(kind, index)

            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)

        self.write_line('</term>', tab_count)

    def compile_subroutine_call(self, tab_count: int) -> None:
        nargs = 0
        object_name = self.tokenizer.get_current_token()

        self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count)

        if not self.tokenizer.is_token_open_parentheses():
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            if self.symbol_table.contains_name(object_name):
                kind = self.symbol_table.kind_of(object_name)
                index = self.symbol_table.index_of(object_name)
                object_name = self.symbol_table.type_of(object_name)
                nargs = 1
                self.vm_writer.write_push(kind, index)

            name = f'{object_name}.{self.tokenizer.get_current_token()}'

            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            self.write_token_and_move_next(self.tokenizer.identifier_xml(), tab_count)

            nargs += self.compile_expression_list(tab_count)
        else:
            name = f'{self.class_name}.{object_name}'
            self.vm_writer.write_push('pointer', 0)
            self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            nargs += self.compile_expression_list(tab_count) + 1

        self.vm_writer.write_call(name, nargs)
        self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count)

    def compile_expression_list(self, tab_count: int) -> int:
        self.write_line('<expressionList>', tab_count)
        count = 0

        if not self.tokenizer.is_token_close_parentheses():
            self.compile_expression(tab_count + 1)
            count += 1

            while self.tokenizer.is_token_comma():
                self.write_token_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
                self.compile_expression(tab_count + 1)
                count += 1

        self.write_line('</expressionList>', tab_count)

        return count
