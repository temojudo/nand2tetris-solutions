from collections import defaultdict


class_vars = {'static', 'field'}


class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.scope_index = defaultdict(int)
        self.while_label_index, self.if_label_index = 0, 0

    def start_subroutine(self) -> None:
        self.subroutine_table = {}
        self.scope_index = defaultdict(int)

    def define(self, name: str, typ: str, kind: str) -> None:
        value = (typ, kind, self.var_count(kind))
        self.increase_var_count(kind)

        if kind in class_vars:
            self.class_table[name] = value
        else:
            self.subroutine_table[name] = value

    def next_if_label_index(self) -> int:
        self.if_label_index += 1
        return self.if_label_index - 1

    def next_while_label_index(self) -> int:
        self.while_label_index += 1
        return self.while_label_index - 1

    def contains_name(self, name: str):
        return name in self.subroutine_table or name in self.class_table

    def var_count(self, kind: str) -> int:
        return self.scope_index[kind]

    def increase_var_count(self, kind: str) -> None:
        self.scope_index[kind] += 1

    def kind_of(self, name: str) -> str:
        if name in self.subroutine_table:
            return self.subroutine_table[name][1]
        else:
            return self.class_table.get(name, ('', '', ''))[1]

    def type_of(self, name: str) -> str:
        if name in self.subroutine_table:
            return self.subroutine_table[name][0]
        else:
            return self.class_table[name][0]

    def index_of(self, name: str) -> int:
        if name in self.subroutine_table:
            return self.subroutine_table[name][2]
        else:
            return self.class_table[name][2]

    def get_num_fields(self) -> int:
        res = 0
        for _, (_, kind, _) in self.class_table.items():
            if kind == 'field':
                res += 1
        return res
