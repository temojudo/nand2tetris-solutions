from enum import Enum
from re import findall, sub, compile
from typing import List, TextIO

from app.constants import DOUBLE_QUOTE

keyword = {
    'class', 'constructor', 'function', 'method', 'field', 'static',
    'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
    'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'
}

symbol = {
    '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
}

specific_symbol_dict = {
    '<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'
}


class StatementType(Enum):
    LET, IF, WHILE, DO, RETURN, NOT_STATEMENT = range(6)


class TokenType(Enum):
    KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST = range(5)


class KeywordType(Enum):
    CLASS, CONSTRUCTOR, FUNCTION, METHOD, FIELD, STATIC, VAR, INT, CHAR, BOOLEAN, VOID, \
        TRUE, FALSE, NULL, THIS, LET, DO, IF, ELSE, WHILE, RETURN = range(len(keyword))


class Tokenizer:

    def __init__(self, file_name: str, out_file_name):
        self.file_name = file_name
        self.out_file_name = out_file_name
        self.file_str = self.parse_file()

        self.quotes = self.get_quote_indexes()
        self.tokens = self.generate_tokens()
        self.curr_token_index = 0

    def write_keyword(self, file: TextIO) -> None:
        file.write(self.keyword_xml() + '\n')

    def write_symbol(self, file: TextIO) -> None:
        file.write(self.symbol_xml() + '\n')

    def write_identifier(self, file: TextIO) -> None:
        file.write(self.identifier_xml() + '\n')

    def write_int_const(self, file: TextIO) -> None:
        file.write(self.int_val_xml() + '\n')

    def write_string_const(self, file: TextIO) -> None:
        file.write(self.string_val_xml() + '\n')

    def write_file(self) -> None:
        with open(self.out_file_name, 'w') as file:
            switcher = {
                TokenType.KEYWORD: self.write_keyword,
                TokenType.SYMBOL: self.write_symbol,
                TokenType.IDENTIFIER: self.write_identifier,
                TokenType.INT_CONST: self.write_int_const,
                TokenType.STRING_CONST: self.write_string_const,
            }

            file.write('<tokens>\n')

            while self.has_more_tokens():
                switcher[self.token_type()](file)
                self.advance()

            file.write('</tokens>\n')

    def reset(self) -> None:
        self.curr_token_index = 0

    def parse_file(self) -> str:
        with open(self.file_name, 'r') as jack_file:
            return sub(compile('(/\\*([^*]|[\r\n]|(\\*+([^*/]|[\r\n])))*\\*+/)|(//.*)'), '', jack_file.read())

    def get_quote_indexes(self) -> List[int]:
        res = [i for i, ch in enumerate(self.file_str) if ch == DOUBLE_QUOTE]
        assert len(res) % 2 == 0, 'Syntax error, num quotes are odd'

        return res

    def generate_tokens(self) -> List[str]:
        all_tokens = findall(r'\w+|[{}()<>.,;=~|&*/+\-\"\[\]]', self.file_str)

        res, i = [], -1
        for token in all_tokens:
            if token == DOUBLE_QUOTE:
                if i % 2 == 0:  # case token is closed quote
                    res.append(DOUBLE_QUOTE + self.file_str[self.quotes[i] + 1: self.quotes[i + 1]] + DOUBLE_QUOTE)
                i += 1
            elif i % 2 == 1:  # case last quote was closed
                res.append(token)

        return res

    def get_current_token(self) -> str:
        return self.tokens[self.curr_token_index]

    def get_current_token_index(self) -> int:
        return self.curr_token_index

    def get_tokens(self) -> List[str]:
        return self.tokens

    def has_more_tokens(self) -> bool:
        return self.curr_token_index < len(self.tokens)

    def advance(self):
        self.curr_token_index += 1

    def token_type(self) -> TokenType:
        if DOUBLE_QUOTE == self.tokens[self.curr_token_index][0]:
            return TokenType.STRING_CONST
        elif self.tokens[self.curr_token_index].isdigit():
            return TokenType.INT_CONST
        elif self.tokens[self.curr_token_index] in keyword:
            return TokenType.KEYWORD
        elif self.tokens[self.curr_token_index] in symbol:
            return TokenType.SYMBOL
        else:
            return TokenType.IDENTIFIER

    def statement(self) -> StatementType:
        switcher = {
            KeywordType.LET: StatementType.LET,
            KeywordType.IF: StatementType.IF,
            KeywordType.WHILE: StatementType.WHILE,
            KeywordType.DO: StatementType.DO,
            KeywordType.RETURN: StatementType.RETURN,
        }

        if self.token_type() == TokenType.KEYWORD and self.keyword() in switcher:
            return switcher[self.keyword()]
        else:
            return StatementType.NOT_STATEMENT

    def keyword(self) -> KeywordType:
        return KeywordType[self.tokens[self.curr_token_index].upper()]

    def symbol(self) -> str:
        token = self.tokens[self.curr_token_index]
        return specific_symbol_dict.get(token, token)

    def identifier(self) -> str:
        return self.tokens[self.curr_token_index]

    def int_val(self) -> int:
        return int(self.tokens[self.curr_token_index])

    def string_val(self) -> str:
        return self.tokens[self.curr_token_index][1: -1]

    def keyword_xml(self) -> str:
        return f'<keyword> {self.tokens[self.curr_token_index]} </keyword>'

    def symbol_xml(self) -> str:
        return f'<symbol> {self.symbol()} </symbol>'

    def identifier_xml(self) -> str:
        return f'<identifier> {self.identifier()} </identifier>'

    def string_val_xml(self) -> str:
        return f'<stringConstant> {self.string_val()} </stringConstant>'

    def int_val_xml(self) -> str:
        return f'<integerConstant> {self.int_val()} </integerConstant>'

    def is_token_open_parentheses(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.SYMBOL and \
               self.symbol() == '('

    def is_token_close_parentheses(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.SYMBOL and \
               self.symbol() == ')'

    def is_token_open_brackets(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.SYMBOL and \
               self.symbol() == '['

    def is_next_token_open_brackets(self) -> bool:
        self.curr_token_index += 1
        res = self.has_more_tokens() and self.token_type() == TokenType.SYMBOL and self.symbol() == '['

        self.curr_token_index -= 1
        return res

    def is_next_token_open_parentheses_or_dot(self) -> bool:
        self.curr_token_index += 1
        res = self.has_more_tokens() and self.token_type() == TokenType.SYMBOL and self.symbol() in '(.'

        self.curr_token_index -= 1
        return res

    def is_token_operation(self) -> bool:
        return self.has_more_tokens() and \
               self.tokens[self.curr_token_index] in '+-*/&|<>='

    def is_token_unary_operation(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.SYMBOL and \
               self.symbol() in '-~'

    def is_token_comma(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.SYMBOL and \
               self.symbol() == ','

    def is_token_semicolon(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.SYMBOL and \
               self.symbol() == ';'

    def is_token_void(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.KEYWORD and \
               self.keyword() == KeywordType.VOID

    def is_token_else(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.KEYWORD and \
               self.keyword() == KeywordType.ELSE

    def is_token_var(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.KEYWORD and \
               self.keyword() == KeywordType.VAR

    def is_token_class_var(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.KEYWORD and \
               self.keyword() in (KeywordType.STATIC,
                                  KeywordType.FIELD)

    def is_token_callable(self) -> bool:
        return self.has_more_tokens() and \
               self.token_type() == TokenType.KEYWORD and \
               self.keyword() in (KeywordType.CONSTRUCTOR,
                                  KeywordType.FUNCTION,
                                  KeywordType.METHOD)
