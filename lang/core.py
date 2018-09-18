from pycparser import c_ast
from pycparser.c_generator import CGenerator


class LangTransformer(CGenerator):
    def __init__(self):
        super().__init__()
        pass

    def visit(self, node):
        print(type(node))
        return super().visit(node)
