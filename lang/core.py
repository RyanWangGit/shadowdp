from pycparser import c_ast
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
import logging
logger = logging.getLogger(__name__)

_code_generator = CGenerator()


def flatten_distance(name, distance):
    """ helper function to flatten the distance"""
    new_distance = list(distance)
    if distance[0] == '*':
        new_distance[0] = '__LANG_distance_{}'.format(name)
    if distance[1] == '*':
        new_distance[1] = '__LANG_distance_shadow_{}'.format(name)
    return new_distance


def extract_variables(expr_node):
    pass


def get_distance(expr_node, types):
    distance_generator = _DistanceGenerator(types)
    return distance_generator.visit(expr_node)


def replace(expr_node):
    pass


class _VariablesExtractor(NodeVisitor):
    pass


class _DistanceGenerator(NodeVisitor):
    def __init__(self, types):
        self._types = types

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_Constant(self, n):
        return '0', '0'

    def visit_ID(self, n):
        return flatten_distance(n.name, self._types[n.name])

    def visit_ArrayRef(self, n):
        aligned, shadow = flatten_distance(n.name.name, self._types[n.name.name][0])
        aligned += '[{}]'.format(_code_generator.visit(n.subscript))
        shadow += '[{}]'.format(_code_generator.visit(n.subscript))
        return aligned, shadow

    def visit_BinaryOp(self, n):
        return ((left + n.op + right) for left, right in zip(self.visit(n.left), self.visit(n.right)))


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

