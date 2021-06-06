# Your code starts here:
from os import listdir
from os.path import isfile, isdir
from typing import List, TextIO

from app.compilation_engine import CompilationEngine
from app.constants import JACK_FILE_EXT, TOKENIZER_FILE_EXT, PARSER_FILE_EXT
from app.tokenizer import Tokenizer, TokenType


def get_out_file_name_for_tokenizer(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + TOKENIZER_FILE_EXT


def get_out_file_name_for_parser(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + PARSER_FILE_EXT


def write_file(file_name: str, lines: List[str]) -> None:
    with open(file_name, 'w') as xml_file:
        xml_file.writelines(lines)


def write_keyword(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write(tokenizer.keyword_xml() + '\n')


def write_symbol(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write(tokenizer.symbol_xml() + '\n')


def write_identifier(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write(tokenizer.identifier_xml() + '\n')


def write_int_const(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write(tokenizer.int_val_xml() + '\n')


def write_string_const(file: TextIO, tokenizer: Tokenizer) -> None:
    file.write(tokenizer.string_val_xml() + '\n')


def analyze_file(file_name: str) -> None:
    tokenizer_file_name = get_out_file_name_for_tokenizer(file_name)
    parser_file_name = get_out_file_name_for_parser(file_name)

    tokenizer = Tokenizer(file_name)
    parser = CompilationEngine(tokenizer, parser_file_name)

    parser.write_file()

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
