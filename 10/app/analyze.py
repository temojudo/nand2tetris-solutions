# Your code starts here:
from os import listdir
from os.path import isfile, isdir
from typing import List, TextIO

from app.constants import JACK_FILE_EXT, TOKENIZER_FILE_EXT, PARSER_FILE_EXT
from app.tokenizer import Tokenizer, TokenType


def get_out_file_name_for_tokenizer(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + TOKENIZER_FILE_EXT


def get_out_file_name_for_parser(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + PARSER_FILE_EXT


# def read_file(file_name: str) -> List[str]:
#     with open(file_name, 'r') as jack_file:
#         return jack_file.readlines()
#
#
# def remove_comments(program_lines: List[str]) -> List[str]:  # doesnt cover all cases
#     res = []
#     multiline_comment_started = False
#
#     for line in program_lines:
#         if '/*' in line:
#             multiline_comment_started = True
#
#         if '*/' in line:
#             multiline_comment_started = False
#             continue
#
#         if not multiline_comment_started:
#             without_inline_comment = line.split('//')[0] if '//' in line else line
#             res.append(without_inline_comment)
#
#     return res


def write_file(file_name: str, lines: List[str]) -> None:
    with open(file_name, 'w') as xml_file:
        xml_file.writelines(lines)


def write_keyword(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write('<keyword> ')
    file.write(tokenizer.keyword()[1])
    file.write(' </keyword>\n')


def write_symbol(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write('<symbol> ')
    file.write(tokenizer.symbol())
    file.write(' </symbol>\n')


def write_identifier(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write('<identifier> ')
    file.write(tokenizer.identifier())
    file.write(' </identifier>\n')


def write_int_const(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write('<integerConstant> ')
    file.write(str(tokenizer.int_val()))
    file.write(' </integerConstant>\n')


def write_string_const(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write('<stringConstant> ')
    file.write(tokenizer.string_val())
    file.write(' </stringConstant>\n')


def analyze_file(file_name: str) -> None:
    tokenizer_file_name = get_out_file_name_for_tokenizer(file_name)
    tokenizer = Tokenizer(file_name)

    switcher = {
        TokenType.KEYWORD: write_keyword,
        TokenType.SYMBOL: write_symbol,
        TokenType.IDENTIFIER: write_identifier,
        TokenType.INT_CONST: write_int_const,
        TokenType.STRING_CONST: write_string_const,
    }

    tokenizer_file = open(tokenizer_file_name, 'w')
    tokenizer_file.write('<tokens>\n')

    while tokenizer.has_more_tokens():
        switcher[tokenizer.token_type()](tokenizer_file, tokenizer)
        tokenizer.advance()

    tokenizer_file.write('</tokens>\n')
    tokenizer_file.close()


def analyze_files(file_names: List[str]) -> None:
    for file_name in file_names:
        analyze_file(file_name)


def get_file_names_from_directory(directory_name: str) -> List[str]:
    return [directory_name.rstrip('/') + '/' + file_name for file_name in listdir(directory_name)
            if JACK_FILE_EXT == file_name[-len(JACK_FILE_EXT):]]


def analyze(jack_file_or_directory_name: str) -> None:
    if isfile(jack_file_or_directory_name):
        file_names = [jack_file_or_directory_name]
    elif isdir(jack_file_or_directory_name):
        file_names = get_file_names_from_directory(jack_file_or_directory_name)
    else:
        raise FileNotFoundError()

    analyze_files(file_names)
