# Your code starts here:
from os import listdir
from os.path import isfile, isdir
from typing import List

from app.compilation_engine import CompilationEngine
from app.constants import JACK_FILE_EXT, TOKENIZER_FILE_EXT, PARSER_FILE_EXT, VM_FILE_EXT
from app.tokenizer import Tokenizer


def get_out_file_name_for_tokenizer(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + TOKENIZER_FILE_EXT


def get_out_file_name_for_parser(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + PARSER_FILE_EXT


def get_out_file_name_for_compiler(input_file_name: str) -> str:
    return input_file_name.rstrip(JACK_FILE_EXT) + VM_FILE_EXT


def compile_file(file_name: str) -> None:
    tokenizer_file_name = get_out_file_name_for_tokenizer(file_name)
    parser_file_name = get_out_file_name_for_parser(file_name)
    compiler_file_name = get_out_file_name_for_compiler(file_name)

    tokenizer = Tokenizer(file_name, tokenizer_file_name)
    tokenizer.write_file()

    tokenizer.reset()
    parser = CompilationEngine(tokenizer, parser_file_name, compiler_file_name)
    parser.write_file()


def compile_files(file_names: List[str]) -> None:
    for file_name in file_names:
        compile_file(file_name)


def get_file_names_from_directory(directory_name: str) -> List[str]:
    return [directory_name.rstrip('/') + '/' + file_name for file_name in listdir(directory_name)
            if JACK_FILE_EXT == file_name[-len(JACK_FILE_EXT):]]


def compile(jack_file_or_directory_name: str) -> None:
    if isfile(jack_file_or_directory_name):
        file_names = [jack_file_or_directory_name]
    elif isdir(jack_file_or_directory_name):
        file_names = get_file_names_from_directory(jack_file_or_directory_name)
    else:
        raise FileNotFoundError()

    compile_files(file_names)
