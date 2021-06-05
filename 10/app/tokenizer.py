from enum import Enum
from re import findall, sub, compile
from typing import List

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


class TokenType(Enum):
    KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST = range(5)


class KeywordType(Enum):
    CLASS, CONSTRUCTOR, FUNCTION, METHOD, FIELD, STATIC, VAR, INT, CHAR, BOOLEAN, VOID, \
        TRUE, FALSE, NULL, THIS, LET, DO, IF, ELSE, WHILE, RETURN = range(len(keyword))


class Tokenizer:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.file_str = self.parse_file()

        self.quotes = self.get_quote_indexes()
        self.tokens = self.generate_tokens()
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

    def keyword(self) -> (KeywordType, str):
        return KeywordType[self.tokens[self.curr_token_index].upper()], self.tokens[self.curr_token_index]

    def symbol(self) -> str:
        token = self.tokens[self.curr_token_index]
        return specific_symbol_dict.get(token, token)

    def identifier(self) -> str:
        return self.tokens[self.curr_token_index]

    def int_val(self) -> int:
        return int(self.tokens[self.curr_token_index])

    def string_val(self) -> str:
        return self.tokens[self.curr_token_index][1: -1]
