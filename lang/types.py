from pycparser.c_parser import CParser
from pycparser.c_generator import CGenerator
from pycparser.c_ast import Node, Constant


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


class TypeSystem(dict):
    _parser = CParser()
    _generator = CGenerator()

    def __getitem__(self, item):
        distance = super().__getitem__(item)
        if distance[0] == '*' or distance[1] == '*':
            distance = distance.copy()
            distance[0] = '__LANG_distance_{}'.format(item) if distance[0] == '*' else distance[0]
            distance[1] = '__LANG_distance_shadow_{}'.format(item) if distance[1] == '*' else distance[1]
        return distance

    def __str__(self):
        return '{{{}}}'.format(
            ', '.join(
                '\'{}\':[{}, {}]'.format(
                    k,
                    self._generator.visit(align) if isinstance(align, Node) else align,
                    self._generator.visit(shadow) if isinstance(shadow, Node) else shadow
                )
                for k, (align, shadow) in super().items()
            )
        )

    def __repr__(self):
        return super().__repr__()
