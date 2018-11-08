from pycparser import c_ast
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
import logging
import copy
from lang.types import TypeSystem, convert_to_ast
logger = logging.getLogger(__name__)

_code_generator = CGenerator()


class _ShadowBranchGenerator(NodeVisitor):
    """ this class generates the shadow branch statement"""
    def __init__(self, shadow_variables, types, conditions):
        """
        :param shadow_variables: the variable list whose shadow distances should be updated
        """
        self._shadow_variables = shadow_variables
        self._distance_generator = _DistanceGenerator(types, conditions)

    # TODO: currently doesn't support declaration in branch
    def visit_Decl(self, node):
        raise NotImplementedError

    def visit_Compound(self, node):
        # TODO: currently doesn't support ArrayRef
        # remove those assignments which has no
        node.block_items = [child for child in node.block_items
                            if isinstance(child, c_ast.Assignment) and child.lvalue.name in self._shadow_variables]
        for child in node:
            if isinstance(child, c_ast.Assignment):
                child.lvalue.name = '__LANG_distance_shadow_{}'.format(child.lvalue.name)
                child.rvalue = convert_to_ast(self._distance_generator.visit(child.rvalue)[1])
            else:
                self.visit(child)


class _ExpressionReplacer(NodeVisitor):
    def __init__(self, types, is_aligned, conditions):
        assert isinstance(types, TypeSystem)
        self._types = types
        self._is_aligned = is_aligned
        self._conditions = conditions

    def _replace(self, node):
        if isinstance(node, c_ast.ArrayRef):
            alignd, shadow = self._types.get_distance(node.name.name, self._conditions)
            distance = alignd if self._is_aligned else shadow
            if distance == '0':
                return node
            else:
                return c_ast.BinaryOp(op='+',
                                      left=node,
                                      right=c_ast.ArrayRef(name=c_ast.ID(name=distance),
                                                           subscript=node.subscript))
        elif isinstance(node, c_ast.ID):
            alignd, shadow = self._types.get_distance(node.name, self._conditions)
            distance = alignd if self._is_aligned else shadow
            if distance == '0':
                return node
            else:
                return c_ast.BinaryOp(op='+',
                                      left=node,
                                      right=c_ast.ID(name=alignd if self._is_aligned else shadow))
        else:
            raise NotImplementedError

    def visit_BinaryOp(self, node):
        if isinstance(node.left, (c_ast.ArrayRef, c_ast.ID)):
            node.left = self._replace(node.left)
        else:
            self.visit(node.left)

        if isinstance(node.right, (c_ast.ArrayRef, c_ast.ID)):
            node.right = self._replace(node.right)
        else:
            self.visit(node.right)

    def visit_UnaryOp(self, node):
        if isinstance(node.expr, (c_ast.ArrayRef, c_ast.ID)):
            node.expr = self._replace(node.expr)
        else:
            self.visit(node.expr)

    def visit(self, node):
        super().visit(node)
        return node


class _ExpressionSimplifier(NodeVisitor):
    """ this class simplifes Ternary operations, e.g., e?c1:c2 + e?c3:c4 -> e?(c1+c2):(c3+c4) """
    def visit_BinaryOp(self, n):
        # TODO
        return n

    def visit_TernaryOp(self, n):
        # TODO
        return n

    def visit_UnaryOp(self, n):
        # TODO
        return n

    def simplify(self, expression):
        ast = convert_to_ast(expression)
        return self.visit(ast)


class _DistanceGenerator(NodeVisitor):
    def __init__(self, types, conditions):
        self._types = types
        self._conditions = conditions
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
        return self._types.get_distance(n.name, self._conditions)

    def visit_ArrayRef(self, n):
        aligned, shadow = self._types.get_distance(n.name.name, self._conditions)
        aligned += '[{}]'.format(_code_generator.visit(n.subscript))
        shadow += '[{}]'.format(_code_generator.visit(n.subscript))
        return [aligned, shadow]

    def visit_BinaryOp(self, n):
        return [self.try_simplify('{} {} {}'.format(left, n.op, right))
                for left, right in zip(self.visit(n.left), self.visit(n.right))]


class LangTransformer(NodeVisitor):
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
        self._condition_stack = []
        # this is a trick to store node's parent, since we cannot dynamically add `parent` attribute
        # to AST nodes. (pycparser uses __slots__ to fix that)
        self._parents = {}
        # indicate if the transformation should be done
        # this is needed since in While statement we might do loop until convergence, in that case we don't need to
        # do transformation
        self._is_to_transform = True
        # this is needed if we add some statements next to the current statement
        # e.g. float eta = havoc(); _v_epsilon = ...;
        # we can't visit the `_v_epsilon = ...;` statement, so we keep track of the inserted statements
        self._inserted = set()

    def visit(self, node):
        if node in self._inserted:
            # ignore the inserted statement
            return
        for child in node:
            self._parents[child] = node
        return super().visit(node)

    def visit_Assignment(self, n):
        code = _code_generator.visit(n)
        logger.debug('{}'.format(code))
        distance_generator = _DistanceGenerator(self._types, self._condition_stack)
        aligned, shadow = distance_generator.visit(n.rvalue)
        self._types.update_distance(n.lvalue.name, aligned, shadow)
        logger.debug('types: {}'.format(self._types))

    def visit_FuncDef(self, n):
        # the start of the transformation
        self._types.clear()
        logger.debug('Start transforming function {} ...'.format(n.decl.name))
        self.generic_visit(n)

        epsilon, size, q, *_ = self._parameters
        inserted = [
            # insert assume(epsilon >= 0)
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('>=', c_ast.ID(epsilon),
                                                               c_ast.Constant('int', 0))])),
            # insert float __LANG_v_epsilon = 0;
            c_ast.Decl(name='__LANG_v_epsilon',
                       type=c_ast.TypeDecl(declname='__LANG_v_epsilon',
                                           type=c_ast.IdentifierType(names=['float']),
                                           quals=[]),
                       init=c_ast.Constant('int', '0'),
                       quals=[], funcspec=[], bitsize=[], storage=[])

        ]

        for name, is_align in self._types.dynamic_variables():
            if name not in self._parameters:
                distance_name = '__LANG_distance_{}{}'.format('' if is_align else 'shadow_', name)
                inserted.append(c_ast.Decl(name=distance_name,
                                           type=c_ast.TypeDecl(declname=distance_name,
                                                               type=c_ast.IdentifierType(names=['float']),
                                                               quals=[]),
                                           init=c_ast.Constant('int', '0'),
                                           quals=[], funcspec=[], bitsize=[], storage=[]))
            elif name == q and is_align:
                # insert float __LANG_distance_q
                inserted.append(c_ast.Decl(name='__LANG_distance_{}'.format(q),
                                           type=c_ast.ArrayDecl(type=c_ast.TypeDecl(declname='__LANG_distance_{}'
                                                                                    .format(q),
                                                                                    type=c_ast.IdentifierType(
                                                                                        names=['float']),
                                                                                    quals=[]),
                                                                dim=c_ast.ID(name=size),
                                                                dim_quals=[]),
                                           init=None,
                                           quals=[], funcspec=[], bitsize=[], storage=[]))
                # insert for(int __LANG_i = 0; __LANG_i < size; __LANG_i++) __LANG_distance_q[i] = havoc();
                inserted.append(c_ast.For(
                    init=c_ast.DeclList(decls=[c_ast.Decl(name='__LANG_i',
                                                          type=c_ast.TypeDecl(declname='__LANG_i',
                                                                              type=c_ast.IdentifierType(names=['int']),
                                                                              quals=[]),
                                                          init=c_ast.Constant('int', '0'),
                                                          quals=[], funcspec=[], bitsize=[], storage=[])]),
                    cond=c_ast.BinaryOp(op='<', left=c_ast.ID('__LANG_i'), right=c_ast.ID(size)),
                    next=c_ast.UnaryOp(op='p++', expr=c_ast.ID('__LANG_i')),
                    stmt=c_ast.Assignment(op='=',
                                          lvalue=c_ast.ArrayRef(name=c_ast.ID('__LANG_distance_{}'.format(q)),
                                                                subscript=c_ast.ID('__LANG_i')),
                                          rvalue=c_ast.FuncCall(name=c_ast.ID(self._func_map['havoc']), args=None))))

        n.body.block_items[:0] = inserted

        # insert assert(__LANG_v_epsilon <= epsilon);
        n.body.block_items.append(c_ast.FuncCall(c_ast.ID(self._func_map['assert']),
                                                 args=c_ast.ExprList([c_ast.BinaryOp('<=', c_ast.ID('__LANG_v_epsilon'),
                                                                                     c_ast.ID(epsilon))])),)

    def visit_Decl(self, n):
        logger.debug('{}'.format(_code_generator.visit_Decl(n)))

        decl_type = n.type
        if isinstance(decl_type, c_ast.FuncDecl):
            # put parameters into type system
            for i, decl in enumerate(decl_type.args.params):
                self._parameters.append(decl.name)
                # TODO: this should be filled by annotation on the argument
                if isinstance(decl.type, c_ast.TypeDecl):
                    self._types.update_distance(decl.name, '0', '0')
                elif isinstance(decl.type, c_ast.ArrayDecl) and i == 2:
                    self._types.update_distance(decl.name, '__LANG_distance_{}'.format(decl.name), '__LANG_distance_{}'.format(decl.name))
            logger.debug('Params: {}'.format(self._parameters))
        if isinstance(decl_type, c_ast.TypeDecl):
            # put variable declaration into type system
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
                        # set the random variable distance
                        self._types.update_distance(n.name, s_d.replace('ALIGNED', d_eta).replace('SHADOW', '0'), '0')
                        # set the normal variable distances
                        for name in self._types.names():
                            if name not in self._random_variables and name not in self._parameters:
                                aligned, shadow = self._types.get_distance(name, self._condition_stack)
                                # if the aligned distance and shadow distance are the same
                                # then there's no need to update the distances
                                if aligned == shadow:
                                    continue
                                else:
                                    self._types.update_distance(name,
                                                                s_e.replace('ALIGNED', '{}'.format(aligned))
                                                                .replace('SHADOW', '{}'.format(shadow)),
                                                                shadow)
                        if self._is_to_transform:
                            n.init = c_ast.FuncCall(c_ast.ID(self._func_map['havoc']), args=None)
                            assert isinstance(self._parents[n], c_ast.Compound)
                            n_index = self._parents[n].block_items.index(n)
                            v_epsilon = '({}) + ({})'.format(s_e.replace('ALIGNED', '__LANG_v_epsilon').replace('SHADOW', '0'),
                                                         s_d.replace('ALIGNED', '({} * (1/({})))'.format(d_eta, sample)).replace('SHADOW', '0'))
                            simplifier = _ExpressionSimplifier()
                            update_v_epsilon = c_ast.Assignment(op='=',
                                                                lvalue=c_ast.ID('__LANG_v_epsilon'),
                                                                rvalue=simplifier.simplify(v_epsilon))
                            self._parents[n].block_items.insert(n_index + 1, update_v_epsilon)
                            self._inserted.add(update_v_epsilon)

                    else:
                        # TODO: function call currently not supported
                        raise NotImplementedError
                else:
                    distance_generator = _DistanceGenerator(self._types, self._condition_stack)
                    aligned, shadow = distance_generator.visit(n.init)
                    self._types.update_distance(n.name, aligned, shadow)
            else:
                self._types.update_distance(n.name, '0', '0')

        elif isinstance(decl_type, c_ast.ArrayDecl):
            # put array variable declaration into type dict
            # TODO: fill in the type
            self._types.update_distance(n.name, '0', '0')

        logger.debug('types: {}'.format(self._types))

    def visit_If(self, n):
        self.visit(n.cond)
        logger.debug('types(before branch): {}'.format(self._types))
        logger.debug('if({})'.format(_code_generator.visit(n.cond)))
        before_types = self._types.copy()
        self._condition_stack.append([n.cond, True])
        self.visit(n.iftrue)
        true_types = self._types
        logger.debug('types(true branch): {}'.format(true_types))
        self._types = before_types
        logger.debug('else')
        if n.iffalse:
            self._condition_stack[-1][1] = False
            self.visit(n.iffalse)
        logger.debug('types(false branch): {}'.format(self._types))
        false_types = self._types.copy()
        self._types.merge(true_types)
        logger.debug('types(after merge): {}'.format(self._types))
        # TODO: use Z3 to solve constraints to decide this value
        to_generate_shadow = True
        if self._is_to_transform:
            aligned_cond = _ExpressionReplacer(self._types, True, self._condition_stack).visit(copy.deepcopy(n.cond))
            shadow_cond = _ExpressionReplacer(self._types, False, self._condition_stack).visit(copy.deepcopy(n.cond))
            # have to generate separate shadow branch
            if to_generate_shadow:
                parent = self._parents[n]
                n_index = parent.block_items.index(n)
                shadow_branch = c_ast.If(cond=shadow_cond,
                                         iftrue=c_ast.Compound(
                                             block_items=copy.deepcopy(n.iftrue.block_items)),
                                         iffalse=c_ast.Compound(
                                             block_items=copy.deepcopy(n.iffalse.block_items)) if n.iffalse else None)
                shadow_branch_generator = _ShadowBranchGenerator(
                    {name for name, is_aligned in self._types.dynamic_variables() if not is_aligned},
                    self._types,
                    self._condition_stack)
                shadow_branch_generator.visit(shadow_branch)
                self._inserted.add(shadow_branch)
                parent.block_items.insert(n_index + 1, shadow_branch)

            # insert assertion
            n.iftrue.block_items.insert(0, c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                                          args=c_ast.ExprList(exprs=[aligned_cond])))
            for name, is_aligned in self._types.diff(true_types):
                if is_aligned:
                    n.iftrue.block_items.append(c_ast.Assignment(op='=',
                                                                 lvalue=c_ast.ID('__LANG_distance_{}'.format(name)),
                                                                 rvalue=true_types.get_raw_distance(name)[0]))
            # insert assertion
            n.iffalse = n.iffalse if n.iffalse else c_ast.Compound(block_items=[])
            n.iffalse.block_items.insert(0, c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                                           args=c_ast.ExprList(exprs=[
                                                               c_ast.UnaryOp(op='!', expr=shadow_cond)
                                                           ])))
            for name, is_aligned in self._types.diff(false_types):
                if is_aligned:
                    n.iffalse.block_items.append(c_ast.Assignment(op='=',
                                                                 lvalue=c_ast.ID('__LANG_distance_{}'.format(name)),
                                                                 rvalue=false_types.get_raw_distance(name)[0]))

        self._condition_stack.pop()

    def visit_While(self, node):
        cur_types = None
        # don't output while doing iterations
        logger.disabled = True
        self._is_to_transform = False
        while cur_types != self._types:
            cur_types = self._types.copy()
            self.generic_visit(node)
        logger.disabled = False
        self._is_to_transform = True
        logger.debug('while({})'.format(_code_generator.visit(node.cond)))
        logger.debug('types(fixed point): {}'.format(self._types))
        self.generic_visit(node)
