from pycparser import c_ast
from pycparser.c_generator import CGenerator
import logging
logger = logging.getLogger(__name__)


class LangTransformer(CGenerator):
    def __init__(self):
        super().__init__()
        self._types = {}
        self._code_generator = CGenerator()

    def visit_Assignment(self, n):
        #print(n.__repr__())

        return super().visit_Assignment(n)

    def visit_FuncDef(self, n):
        #print(n.__repr__())
        return super().visit_FuncDef(n)

    def visit_Decl(self, node, no_type=False):
        decl_type = node.type
        if isinstance(decl_type, c_ast.FuncDecl):
            # put parameters into types dict
            for decl in decl_type.args.params:
                # TODO: fill in the type
                if isinstance(decl.type, c_ast.TypeDecl):
                    self._types[decl.name] = decl.type.type.names[0]
                elif isinstance(decl.type, c_ast.ArrayDecl):
                    self._types[decl.name] = decl.type.type.type.names[0] + ' array'
        elif isinstance(decl_type, c_ast.TypeDecl):
            # put variable declaration into type dict
            # TODO: fill in the type
            self._types[node.name] = decl_type.type.names[0]
        elif isinstance(decl_type, c_ast.ArrayDecl):
            # put array variable declaration into type dict
            # TODO: fill in the type
            self._types[node.name] = decl_type.type.type.names[0] + ' array'

        code = self._code_generator.visit_Decl(node) + ';'
        logger.info(code)
        logger.info('types: {}'.format(self._types))
        return code
