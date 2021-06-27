from app.tokenizer import KeywordType

symbol_to_alu_command = {
    '*': 'call Math.multiply 2', '/': 'call Math.divide 2',
    '+': 'add', '-': 'sub', '=': 'eq', '~': 'not',
    '|': 'or', '&gt': 'gt', '@lt': 'lt', '@amp': 'amp',
    '>': 'gt', '<': 'lt', '&': 'and'
}

var_types_to_segments = {'field': 'this'}


def keyword_type_to_segment_str(keyword: KeywordType) -> str:
    return keyword.__str__().lower()


class VMWriter:
    def __init__(self, out_file_name: str):
        self.file = open(out_file_name, 'w')

    def write_push(self, segment: str, index: int) -> None:
        self.file.write(f'push {var_types_to_segments.get(segment, segment)} {index}\n')

    def write_pop(self, segment: str, index: int) -> None:
        self.file.write(f'pop {var_types_to_segments.get(segment, segment)} {index}\n')

    def write_alu(self, symbol: str):
        self.file.write(f'{symbol_to_alu_command.get(symbol, symbol)}\n')

    def write_label(self, label: str, index: int) -> None:
        self.file.write(f'label {label}{index}\n')

    def write_goto(self, label: str, index: int) -> None:
        self.file.write(f'goto {label}{index}\n')

    def write_if_goto(self, label: str, index: int) -> None:
        self.file.write(f'if-goto {label}{index}\n')

    def write_function(self, class_name: str, function_name: str, nargs: int) -> None:
        self.file.write(f'function {class_name}.{function_name} {nargs}\n')

    def write_call(self, name: str, nargs: int) -> None:
        self.file.write(f'call {name} {nargs}\n')

    def write_return(self) -> None:
        self.file.write(f'return\n')

    def write_string(self, value: str) -> None:
        self.write_push('constant', len(value))
        self.write_call('String.new', 1)

        for ch in value:
            self.write_push('constant', ord(ch))
            self.write_call('String.appendChar', 2)

    def write_keyword(self, keyword: str) -> None:
        if keyword == 'true':
            self.write_push('constant', 0)
            self.write_alu('not')
        elif keyword in ('false', 'null'):
            self.write_push('constant', 0)
        elif keyword == 'this':
            self.write_push('pointer', 0)

    def write_method_header(self) -> None:
        self.write_push('argument', 0)
        self.write_pop('pointer', 0)

    def write_constructor_header(self, size: int) -> None:
        self.write_push('constant', size)
        self.write_call('Memory.alloc', 1)
        self.write_pop('pointer', 0)

    def close_file(self):
        self.file.close()
