from pycparser import c_ast
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
import logging
logger = logging.getLogger(__name__)


def extract_variables(expr_node):
    pass


def get_distance(expr_node):
    pass


def replace(expr_node):
    pass


class _VariablesExtractor(NodeVisitor):
    pass


class _ExpressionDistance(NodeVisitor):
    pass


class _ExpressionReplacer(CGenerator):
    pass


class LangTransformer(CGenerator):
    def __init__(self, function_map=None):
        super().__init__()
        if not function_map:
            self._func_map = {
                'assert': 'assert',
                'assume': 'assume',
                'havoc': 'havoc',
            }
        else:
            assert 'assert' in function_map and 'assume' in function_map and 'havoc' in function_map
            self._func_map = function_map
        self._types = {}
        self._code_generator = CGenerator()
        self._reserved_params = [None, None, None]

    def visit_Assignment(self, n):
        #print(n.__repr__())

        return super().visit_Assignment(n)

    def visit_FuncDef(self, n):
        # the start of the transformation
        self._types = {}
        logger.info('Start transforming function {} ...'.format(n.decl.name))
        return super().visit_FuncDef(n)

    def visit_Decl(self, n, no_type=False):
        code = self._code_generator.visit_Decl(n)
        transformed_code = code
        logger.info(code + ';')

        decl_type = n.type
        if isinstance(decl_type, c_ast.FuncDecl):
            # put parameters into types dict
            for i, decl in enumerate(decl_type.args.params):
                if i < 3:
                    self._reserved_params[i] = decl.name
                # TODO: fill in the type
                if isinstance(decl.type, c_ast.TypeDecl):
                    self._types[decl.name] = [[0, 0], decl.type.type.names[0]]
                elif isinstance(decl.type, c_ast.ArrayDecl):
                    self._types[decl.name] = [[0, 0], 'list ' + decl.type.type.type.names[0]]
            logger.debug('Reserved Params: {}'.format(self._reserved_params))
        if isinstance(decl_type, c_ast.TypeDecl):
            # put variable declaration into type dict
            # TODO: fill in the type
            if n.init:
                # TODO: get distance of the expression
                self._types[n.name] = [[0, 0], decl_type.type.names[0]]
            else:
                self._types[n.name] = [[0, 0], decl_type.type.names[0]]


        elif isinstance(decl_type, c_ast.ArrayDecl):
            # put array variable declaration into type dict
            # TODO: fill in the type
            self._types[n.name] = [[0, 0], 'list ' + decl_type.type.type.names[0]]

        logger.info('types: {}'.format(self._types))
        return transformed_code

