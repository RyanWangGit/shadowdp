from pycparser.c_parser import CParser
from pycparser.c_generator import CGenerator
from pycparser import c_ast


def simplify_distance(expr, condition, is_true):
    """ simplifies distance expression string, e.g. expr="e1 ? e2 ? c1 : c2 : c3", condition=e2, is_true=True
    this function returns "e1 ? c1 : c3"
    :param expr: The expression to simplify
    :param condition: The condition for simplification.
    :param is_true: Indicates the condition is true or false.
    :return: Simplified string.
    """
    # TODO: implement this
    return expr


class TypeSystem:
    _parser = CParser()
    _generator = CGenerator()
    _EXPR_NODES = (c_ast.BinaryOp, c_ast.TernaryOp, c_ast.UnaryOp, c_ast.ID, c_ast.Constant, c_ast.ArrayRef)

    def __init__(self, types=None):
        if types:
            self._types = types
        else:
            self._types = {}

    def __str__(self):
        # convert AST representation to code representation for better human-readability
        return '{{{}}}'.format(
            ', '.join('{}: [{}, {}]'.format(name,
                                            aligned if aligned == '*' else self._generator.visit(aligned),
                                            shadow if shadow == '*' else self._generator.visit(shadow))
                      for name, (aligned, shadow) in self._types.items()
                      )
        )

    def __repr__(self):
        return self._types.__repr__()

    def copy(self):
        return TypeSystem(self._types.copy())

    def clear(self):
        self._types.clear()

    def names(self):
        return self._types.keys()

    def _convert_to_ast(self, expression):
        # this is a trick since pycparser cannot parse expression directly
        ast = self._parser.parse('int placeholder(){{{};}}'.format(expression)).ext[0].body.block_items[0]
        return ast

    def _is_node_equal(self, node_1, node_2):
        """ check if two expression AST nodes are equal since pycparser doesn't provide such property
        :param node_1: First expression node
        :param node_2: Second expression node
        :return: Boolean
        """
        # TODO: implement this
        assert isinstance(node_1, self._EXPR_NODES) and isinstance(node_2, self._EXPR_NODES)
        return False

    def apply(self, condition, is_true):
        """ apply the condition to all distances
        :param condition:
        :param is_true:
        :return:
        """
        # TODO: implement this
        pass

    def get_distance(self, name):
        aligned, shadow = self._types[name]
        return '__LANG_distance_{}'.format(name) if aligned == '*' else self._generator.visit(aligned), \
               '__LANG_distance_shadow_{}'.format(name) if shadow == '*' else self._generator.visit(shadow)

    def update_distance(self, name, aligned, shadow):
        aligned = '*' if aligned == '*' else self._convert_to_ast(aligned)
        shadow = '*' if shadow == '*' else self._convert_to_ast(shadow)
        if name not in self._types:
            self._types[name] = [aligned, shadow]
        else:
            cur_aligned, cur_shadow = self._types[name]
            if not self._is_node_equal(cur_aligned, aligned):
                self._types[name][0] = aligned
            if not self._is_node_equal(cur_shadow, shadow):
                self._types[name][1] = shadow
