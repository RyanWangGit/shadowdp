from pycparser import c_ast
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
import logging
from lang.types import TypeSystem
logger = logging.getLogger(__name__)

_code_generator = CGenerator()


class _DistanceGenerator(NodeVisitor):
    def __init__(self, types):
        self._types = types
        assert isinstance(self._types, TypeSystem)

    def try_simplify(self, expr):
        from sympy import simplify
        try:
            expr = str(simplify(expr))
        finally:
            return expr

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_Constant(self, n):
        return ['0', '0']

    def visit_ID(self, n):
        return self._types.get_distance(n.name)

    def visit_ArrayRef(self, n):
        aligned, shadow = self._types.get_distance(n.name.name)
        aligned += '[{}]'.format(_code_generator.visit(n.subscript))
        shadow += '[{}]'.format(_code_generator.visit(n.subscript))
        return [aligned, shadow]

    def visit_BinaryOp(self, n):
        return [self.try_simplify('{} {} {}'.format(left, n.op, right))
                for left, right in zip(self.visit(n.left), self.visit(n.right))]


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
        self._types = TypeSystem()
        self._parameters = []
        self._random_variables = set()

    def visit_Assignment(self, n):
        code = _code_generator.visit(n)
        logger.debug('{}{}'.format(self._make_indent(), code))
        distance_generator = _DistanceGenerator(self._types)
        aligned, shadow = distance_generator.visit(n.rvalue)
        self._types.update_distance(n.lvalue.name, aligned, shadow)
        logger.debug('{}types: {}'.format(self._make_indent(), self._types))
        return code

    def visit_FuncDef(self, n):
        # the start of the transformation
        self._types.clear()
        logger.debug('Start transforming function {} ...'.format(n.decl.name))
        return super().visit_FuncDef(n)

    def visit_Decl(self, n, no_type=False):
        code = _code_generator.visit_Decl(n)
        transformed_code = code
        logger.debug('{}{}'.format(self._make_indent(), code))

        decl_type = n.type
        if isinstance(decl_type, c_ast.FuncDecl):
            # put parameters into types dict
            for decl in decl_type.args.params:
                self._parameters.append(decl.name)
                # TODO: this should be filled by annotation on the argument
                if isinstance(decl.type, c_ast.TypeDecl):
                    self._types.update_distance(decl.name, '0', '0')
                elif isinstance(decl.type, c_ast.ArrayDecl):
                    self._types.update_distance(decl.name, '*', '*')
            logger.debug('Params: {}'.format(self._parameters))
        if isinstance(decl_type, c_ast.TypeDecl):
            # put variable declaration into type dict
            # TODO: fill in the type
            if n.init:
                if isinstance(n.init, c_ast.FuncCall):
                    if n.init.name.name == 'Lap':
                        # random variable declaration
                        self._random_variables.add(n.name)
                        logger.debug('Random variables: {}'.format(self._random_variables))
                        sample = _code_generator.visit(n.init.args.exprs[0])
                        assert isinstance(n.init.args.exprs[1], c_ast.Constant) and \
                               n.init.args.exprs[1].type == 'string', \
                            'The second argument of Lap function must be string annotation'
                        s_e, s_d, d_eta, *_ = map(lambda x: x.strip(), n.init.args.exprs[1].value[1:-1].split(';'))
                        s_d = s_d.replace('ALIGNED', d_eta).replace('SHADOW', '0')
                        # set the random variable distance
                        self._types.update_distance(n.name, s_d, '0')
                        # set the normal variable distances
                        for name in self._types.names():
                            if name not in self._random_variables and name not in self._parameters:
                                aligned, shadow = self._types.get_distance(name)
                                # if the aligned distance and shadow distance are the same
                                # then there's no need to update the distances
                                if aligned == shadow:
                                    continue
                                else:
                                    self._types.update_distance(name,
                                                                s_e.replace('ALIGNED', '{}'.format(aligned))
                                                                .replace('SHADOW', '{}'.format(shadow)),
                                                                shadow)

                    else:
                        # TODO: function call currently not supported
                        raise NotImplementedError
                else:
                    distance_generator = _DistanceGenerator(self._types)
                    aligned, shadow = distance_generator.visit(n.init)
                    self._types.update_distance(n.name, aligned, shadow)
            else:
                self._types.update_distance(n.name, '0', '0')

        elif isinstance(decl_type, c_ast.ArrayDecl):
            # put array variable declaration into type dict
            # TODO: fill in the type
            self._types.update_distance(n.name, '0', '0')

        logger.debug('{}types: {}'.format(self._make_indent(), self._types))
        return transformed_code

    def visit_If(self, n):
        s = 'if ('
        if n.cond:
            s += self.visit(n.cond)
        s += ')\n'
        logger.debug('{}types(before branch): {}'.format(self._make_indent(), self._types))
        logger.debug('{}{}'.format(self._make_indent(), s.strip()))

        before_types = self._types.copy()
        s += self._generate_stmt(n.iftrue, add_indent=True)
        true_types = self._types
        logger.debug('{}types(true branch): {}'.format(self._make_indent() + ' ' * 2, true_types))
        self._types = before_types
        logger.debug('{}else'.format(self._make_indent()))
        if n.iffalse:
            s += self._make_indent() + 'else\n'
            s += self._generate_stmt(n.iffalse, add_indent=True)
        false_types = self._types
        logger.debug('{}types(false branch): {}'.format(self._make_indent() + ' ' * 2, false_types))
        # TODO: merge the types
        logger.debug('{}types(after merge): {}'.format(self._make_indent(), self._types))

        return s

