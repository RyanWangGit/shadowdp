# MIT License
#
# Copyright (c) 2018-2019 Yuxin (Ryan) Wang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sympy as sp
import logging
import copy
import re
from pycparser import c_ast
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
from shadowdp.types import TypeSystem, convert_to_ast, is_node_equal
from shadowdp.exceptions import *
logger = logging.getLogger(__name__)

_code_generator = CGenerator()


class _ExpressionFinder(NodeVisitor):
    """ this class find a specific node in the expression"""
    def __init__(self, check_func):
        self._check_func = check_func

    def generic_visit(self, node):
        if self._check_func(node):
            return node
        else:
            for child in node:
                node = self.generic_visit(child)
                if node:
                    return node


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
            aligned, shadow = self._types.get_distance(node.name, self._conditions)
            distance = aligned if self._is_aligned else shadow
            if distance == '0':
                return node
            else:
                return c_ast.BinaryOp(op='+',
                                      left=node,
                                      right=c_ast.ID(name=aligned if self._is_aligned else shadow))
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
        if isinstance(n.left, c_ast.TernaryOp) and isinstance(n.right, c_ast.TernaryOp) and is_node_equal(n.left.cond, n.right.cond):
            return c_ast.TernaryOp(cond=n.left.cond,
                                   iftrue=c_ast.BinaryOp(op=n.op, left=n.left.iftrue, right=n.right.iftrue),
                                   iffalse=c_ast.BinaryOp(op=n.op, left=n.left.iffalse, right=n.right.iffalse))
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
        return '0', '0'

    def visit_ID(self, n):
        align, shadow = self._types.get_distance(n.name, self._conditions)
        align = '(__SHADOWDP_ALIGNED_{0} - {0})'.format(n.name) if align == '*' else align
        shadow = '(__SHADOWDP_SHADOW_{0} - {0})'.format(n.name) if shadow == '*' else shadow
        return align, shadow

    def visit_ArrayRef(self, n):
        varname, subscript = n.name.name, _code_generator.visit(n.subscript)
        align, shadow = self._types.get_distance(n.name.name, self._conditions)
        align = '(__SHADOWDP_ALIGNED_{0}[{1}] - {0}[{1}])'.format(varname, subscript) if align == '*' else align
        shadow = '(__SHADOWDP_SHADOW_{0}[{1}] - {0}[{1}])'.format(varname, subscript) if shadow == '*' else shadow
        return align, shadow

    def visit_BinaryOp(self, n):
        return [self.try_simplify('{} {} {}'.format(left, n.op, right))
                for left, right in zip(self.visit(n.left), self.visit(n.right))]


class ShadowDPTransformer(NodeVisitor):
    """ Traverse the AST and do necessary transformations on the AST according to the typing rules."""
    def __init__(self, function_map=None, set_epsilon=None):
        """ Initialize the transformer.
        :param function_map: A dict containing a mapping from logical commands (assert / assume / havoc)
        to actual commands (e.g., __VERIFIER_assert in CPAChecker), this is an abstraction for use with other
        verification tools that may have other names for assert / assume / havoc commands.
        :param set_epsilon: boolean value indicating if we want to set epsilon to 1 to overcome the non-linearity issue.
        """
        super().__init__()

        # set default value for function_map
        if not function_map:
            self._func_map = {
                'assert': 'assert',
                'assume': 'assume',
                'havoc': 'havoc',
            }
        else:
            if not isinstance(function_map, dict):
                raise ValueError
            if not ('assert' in function_map and 'assume' in function_map and 'havoc' in function_map):
                raise ValueError
            self._func_map = function_map

        self._set_epsilon = set_epsilon
        self._types = TypeSystem()
        self._parameters = []
        self._random_variables = set()
        # indicator that all at most one record can differ or records can differ
        self._one_differ = True
        # use a stack to keep track of the conditions so that we know we're inside a true branch or false branch
        self._condition_stack = []
        # we keep tracks of the parent of each node since pycparser doesn't provide this feature, this is useful
        # for easy trace back
        self._parents = {}
        # indicate if level of loop statements, this is needed since in While statement we might loop until convergence,
        # before convergence we shouldn't do transformation
        self._loop_level = 0
        # this is needed if we add some statements next to the current statement
        # e.g. float eta = havoc(); _v_epsilon = ...;
        # we shouldn't visit the `_v_epsilon = ...;` statement node, so we keep track of the inserted statements
        # to avoid them
        self._inserted = set()

    def visit(self, node):
        if node in self._inserted:
            # ignore the inserted statement
            return
        for child in node:
            self._parents[child] = node
        return super().visit(node)

    def visit_FuncDef(self, node):
        # the start of the transformation
        self._types.clear()
        logger.info('Start transforming function {} ...'.format(node.decl.name))

        # first pickup the annotation for parameters
        first_statement = node.body.block_items.pop(0)
        if not (isinstance(first_statement, c_ast.Constant) and first_statement.type == 'string'):
            raise NoParameterAnnotationError(first_statement.coord)
        annotation = first_statement.value[1:-1]
        if annotation not in ('ALL_DIFFER', 'ONE_DIFFER'):
            raise ValueError('Annotation for sensitivity should be either \'ALL_DIFFER\' or \'ONE_DIFFER\'')

        self._one_differ = True if annotation == 'ONE_DIFFER' else False

        # visit children
        self.generic_visit(node)

        # get the names of parameters
        epsilon, size, q, *_ = self._parameters

        insert_statements = [
            # insert assume(epsilon > 0)
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('>', c_ast.ID(epsilon),
                                                               c_ast.Constant('int', 0))])),
            # insert assume(size > 0)
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('>', c_ast.ID(size),
                                                               c_ast.Constant('int', 0))])),

            # insert float __SHADOWDP_v_epsilon = 0;
            c_ast.Decl(name='__SHADOWDP_v_epsilon',
                       type=c_ast.TypeDecl(declname='__SHADOWDP_v_epsilon',
                                           type=c_ast.IdentifierType(names=['float']),
                                           quals=[]),
                       init=c_ast.Constant('int', '0'),
                       quals=[], funcspec=[], bitsize=[], storage=[]),
        ]

        if self._one_differ:
            insert_statements.append(
                # insert assume(__SHADOWDP_index >= 0);
                c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                               args=c_ast.ExprList([c_ast.BinaryOp('>=', c_ast.ID('__SHADOWDP_index'),
                                                                   c_ast.Constant('int', 0))])),
            )
            insert_statements.append(
                # insert assume(__SHADOWDP_index < size);
                c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                               args=c_ast.ExprList([c_ast.BinaryOp('<', c_ast.ID('__SHADOWDP_index'),
                                                                   c_ast.ID(size))]))
            )
            # insert parameter __SHADOWDP_index
            node.decl.type.args.params.append(
                c_ast.Decl(name='__SHADOWDP_index',
                           type=c_ast.TypeDecl(declname='__SHADOWDP_index',
                                               type=c_ast.IdentifierType(names=['int']),
                                               quals=[]),
                           init=None,
                           quals=[], funcspec=[], bitsize=[], storage=[])
            )

        # add declarations / new parameters for dynamically tracked variables
        for name, distances in self._types.variables():
            for index, distance in enumerate(distances):
                if distance == '*':
                    # if it is a dynamically tracked local variable, add declarations
                    version = 'ALIGNED' if index == 0 else 'SHADOW'
                    if name not in self._parameters:
                        varname = '__SHADOWDP_{}_{}'.format(version, name)
                        insert_statements.append(
                            c_ast.Decl(name=varname,
                                       type=c_ast.TypeDecl(declname=varname,
                                                           type=c_ast.IdentifierType(names=['float']), quals=[]),
                                       init=c_ast.Constant('int', '0'), quals=[], funcspec=[], bitsize=[], storage=[]))
                    # if it is a dynamically tracked parameter, add new parameters
                    else:
                        # TODO: should be able to detect the type of parameters
                        if name != q:
                            raise NotImplementedError
                        varname = '__SHADOWDP_{}_{}'.format(version, q)
                        node.decl.type.args.params.append(
                            c_ast.Decl(name=varname,
                                       type=c_ast.ArrayDecl(
                                           type=c_ast.TypeDecl(declname=varname, type=c_ast.IdentifierType(
                                               names=['float']), quals=[]), dim=None, dim_quals=[]),
                                       init=None,
                                       quals=[], funcspec=[], bitsize=[], storage=[])
                        )

        # prepend the inserted statements
        node.body.block_items[:0] = insert_statements

        # insert assert(__SHADOWDP_v_epsilon <= epsilon);
        epsilon_node = c_ast.Constant(type='float', value=1.0) if self._set_epsilon else c_ast.ID(epsilon)
        node.body.block_items.append(c_ast.FuncCall(c_ast.ID(self._func_map['assert']),
                                                    args=c_ast.ExprList(
                                                        [c_ast.BinaryOp('<=', c_ast.ID('__SHADOWDP_v_epsilon'),
                                                                        epsilon_node)])), )

    def visit_Assignment(self, node):
        logger.debug('Line {}: {}'.format(str(node.coord.line), _code_generator.visit(node)))
        # get new distance from the assignment expression (T-Asgn)
        aligned, shadow = _DistanceGenerator(self._types, self._condition_stack).visit(node.rvalue)
        self._types.update_distance(node.lvalue.name, aligned, shadow)
        logger.debug('types: {}'.format(self._types))

    def visit_Decl(self, node):
        logger.debug('Line {}: {}'.format(str(node.coord.line), _code_generator.visit(node)))

        # if declarations are in function parameters, store distance into type system
        if isinstance(node.type, c_ast.FuncDecl):
            for param_index, decl in enumerate(node.type.args.params):
                self._parameters.append(decl.name)
                # TODO: this should be filled by annotation on the parameter
                # query variable has type (*, *)
                if isinstance(decl.type, c_ast.ArrayDecl) and param_index == 2:
                    self._types.update_distance(decl.name, '*', '*')
                # other variables have type (0, 0)
                elif isinstance(decl.type, c_ast.TypeDecl):
                    self._types.update_distance(decl.name, '0', '0')

            logger.debug('Params: {}'.format(self._parameters))

        # if declarations are in function body, store distance into type system
        elif isinstance(node.type, c_ast.TypeDecl):
            # if no initial value is given, default to (0, 0)
            if not node.init:
                self._types.update_distance(node.name, '0', '0')
            # else update the distance to the distance of initial value (T-Asgn)
            elif isinstance(node.init, (c_ast.ExprList, c_ast.Constant)):
                aligned, shadow = _DistanceGenerator(self._types, self._condition_stack).visit(node.init)
                self._types.update_distance(node.name, aligned, shadow)
            # if it is random variable declaration
            elif isinstance(node.init, c_ast.FuncCall) and node.init.name.name == 'Lap':
                self._random_variables.add(node.name)
                logger.debug('Random variables: {}'.format(self._random_variables))
                if not (isinstance(node.init.args.exprs[1], c_ast.Constant) and
                        node.init.args.exprs[1].type == 'string'):
                    raise NoSamplingAnnotationError

                # get the annotation for sampling command
                selector, distance_eta, *_ = map(lambda x: x.strip(), node.init.args.exprs[1].value[1:-1].split(';'))
                # set the random variable distance
                self._types.update_distance(node.name, distance_eta, '0')

                # update distances of normal variables according to the selector
                for name, (align, shadow) in self._types.variables(self._condition_stack):
                    # if the aligned distance and shadow distance are the same
                    # then there's no need to update the distances
                    if align != shadow and name not in self._random_variables and name not in self._parameters:
                        self._types.update_distance(
                            name,
                            selector.replace('SHADOW', '({})'.format(shadow)).replace('ALIGNED', '({})'.format(align)),
                            shadow)

                if self._loop_level == 0:
                    # transform sampling command to havoc command
                    node.init = c_ast.FuncCall(c_ast.ID(self._func_map['havoc']), args=None)

                    # insert cost variable update statement
                    assert isinstance(self._parents[node], c_ast.Compound)
                    n_index = self._parents[node].block_items.index(node)
                    scale = _code_generator.visit(node.init.args.exprs[0])
                    # incorporate epsilon = 1 approach
                    if self._set_epsilon:
                        epsilon, *_ = self._parameters
                        scale = scale.replace(epsilon, '1.0')

                    # TODO: maybe create a specialized simplifier for this scenario
                    pieces = re.compile('\?|\:').split(distance_eta)
                    new_pieces = []
                    for piece in pieces:
                        if '=' not in piece and '>' not in piece and '<' not in piece \
                                and '|' not in piece and '&' not in piece:
                            cost = '({} * (1/({})))'.format(piece, scale)
                            # try simplify the cost expression
                            try:
                                cost = str(sp.simplify(cost))
                            except Exception:
                                pass
                            new_pieces.append(cost)
                        else:
                            pass

                    v_epsilon = '({}) + ({})'.format(
                        selector.replace('SHADOW', '0').replace('ALIGNED', '__SHADOWDP_v_epsilon'),
                        cost)
                    simplifier = _ExpressionSimplifier()
                    update_v_epsilon = c_ast.Assignment(op='=',
                                                        lvalue=c_ast.ID('__LANG_v_epsilon'),
                                                        rvalue=simplifier.simplify(v_epsilon))
                    self._parents[node].block_items.insert(n_index + 1, update_v_epsilon)
                    self._inserted.add(update_v_epsilon)
            else:
                raise NotImplementedError('Initial value currently not supported: {}'.format(node.init))

        elif isinstance(node.type, c_ast.ArrayDecl):
            # put array variable declaration into type dict
            # TODO: fill in the type
            self._types.update_distance(node.name, '0', '0')

        else:
            raise NotImplementedError('Declaration statement currently not supported: {}'.format(node))

        logger.debug('types: {}'.format(self._types))

    def visit_If(self, n):
        logger.debug('types(before branch): {}'.format(self._types))
        logger.debug('if({})'.format(_code_generator.visit(n.cond)))
        before_types = self._types.copy()
        self._condition_stack.append([n.cond, True])
        # to be used in if branch transformation assert(e^aligned);
        aligned_true_cond = _ExpressionReplacer(before_types, True, self._condition_stack).visit(
            copy.deepcopy(n.cond))
        self.visit(n.iftrue)
        true_types = self._types
        logger.debug('types(true branch): {}'.format(true_types))
        self._types = before_types.copy()
        logger.debug('else')
        self._condition_stack[-1][1] = False
        if n.iffalse:
            self.visit(n.iffalse)
        # to be used in else branch transformation assert(not (e^aligned));
        aligned_false_cond = _ExpressionReplacer(before_types, True, self._condition_stack).visit(
            copy.deepcopy(n.cond))
        logger.debug('types(false branch): {}'.format(self._types))
        false_types = self._types.copy()
        self._types.merge(true_types)
        logger.debug('types(after merge): {}'.format(self._types))
        # TODO: use Z3 to solve constraints to decide this value
        to_generate_shadow = True
        if self._loop_level == 0:
            # have to generate separate shadow branch
            if to_generate_shadow:
                shadow_cond = _ExpressionReplacer(self._types, False, self._condition_stack).visit(
                    copy.deepcopy(n.cond))
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
                                                          args=c_ast.ExprList(exprs=[aligned_true_cond])))

            # if the expression contains `query` variable, add an assume function on dq
            exp_checker = _ExpressionFinder(
                lambda node: isinstance(node, c_ast.ArrayRef) and
                             node.name.name == '__LANG_distance_{}'.format(self._parameters[2]))
            query_distance_node = exp_checker.visit(aligned_true_cond)
            if query_distance_node:
                # insert assume(__LANG_distance_q[i] >= -1 && __LANG_distance_q[i] <= 1)
                # TODO: should change according to programmer
                assume_function = \
                    c_ast.FuncCall(name=c_ast.ID(self._func_map['assume']),
                                   args=c_ast.ExprList(
                                       exprs=[c_ast.BinaryOp(op='&&',
                                                             left=c_ast.BinaryOp(op='>=',
                                                                                 left=query_distance_node,
                                                                                 right=c_ast.Constant('int', '-1')),
                                                             right=c_ast.BinaryOp(op='<=',
                                                                                  left=query_distance_node,
                                                                                  right=c_ast.Constant('int', '1')))]))
                n.iftrue.block_items.insert(0, assume_function)

            for name, is_aligned in self._types.diff(true_types):
                if is_aligned:
                    n.iftrue.block_items.append(c_ast.Assignment(op='=',
                                                                 lvalue=c_ast.ID('__LANG_distance_{}'.format(name)),
                                                                 rvalue=true_types.get_raw_distance(name)[0]))
            # create else branch if doesn't exist
            n.iffalse = n.iffalse if n.iffalse else c_ast.Compound(block_items=[])
            # add assume to else branch
            # insert assertion
            n.iffalse.block_items.insert(0, c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                                           args=c_ast.ExprList(exprs=[
                                                               c_ast.UnaryOp(op='!', expr=aligned_false_cond)
                                                           ])))
            query_distance_node = exp_checker.visit(aligned_false_cond)
            if query_distance_node:
                # insert assume(__LANG_distance_q[i] >= -1 && __LANG_distance_q[i] <= 1)
                # TODO: should change according to programmer
                assume_function = \
                    c_ast.FuncCall(name=c_ast.ID(self._func_map['assume']),
                                   args=c_ast.ExprList(
                                       exprs=[c_ast.BinaryOp(op='&&',
                                                             left=c_ast.BinaryOp(op='>=',
                                                                                 left=query_distance_node,
                                                                                 right=c_ast.Constant('int', '-1')),
                                                             right=c_ast.BinaryOp(op='<=',
                                                                                  left=query_distance_node,
                                                                                  right=c_ast.Constant('int', '1')))]))
                n.iffalse.block_items.insert(0, assume_function)
            for name, is_aligned in self._types.diff(false_types):
                if is_aligned:
                    n.iffalse.block_items.append(c_ast.Assignment(op='=',
                                                                  lvalue=c_ast.ID('__LANG_distance_{}'.format(name)),
                                                                  rvalue=false_types.get_raw_distance(name)[0]))

        self._condition_stack.pop()

    def visit_While(self, node):
        cur_types = None
        # don't output logs while doing iterations
        logger.disabled = True
        self._loop_level += 1
        while cur_types != self._types:
            cur_types = self._types.copy()
            self.generic_visit(node)
            self._types.merge(cur_types)
        logger.disabled = False
        self._loop_level -= 1
        logger.debug('while({})'.format(_code_generator.visit(node.cond)))
        logger.debug('types(fixed point): {}'.format(self._types))
        aligned_cond = _ExpressionReplacer(self._types, True, self._condition_stack).visit(
            copy.deepcopy(node.cond))
        assertion = c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                   args=c_ast.ExprList(exprs=[aligned_cond]))
        self._inserted.add(assertion)
        node.stmt.block_items.insert(0, assertion)
        self.generic_visit(node)
